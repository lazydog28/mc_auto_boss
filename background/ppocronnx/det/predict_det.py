# Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os

import cv2
import numpy as np

import time

import onnxruntime as ort
import logging
from ppocronnx.utility import get_model_data, get_model_data_from_path
from .preprocess import preprocess_op
from .postprocess import DBPostProcess

logger = logging
model_file = 'det.onnx'


def draw_text_det_res(dt_boxes, img):
    src_im = img.copy()
    for box in dt_boxes:
        box = np.array(box).astype(np.int32).reshape(-1, 2)
        cv2.polylines(src_im, [box], True, color=(255, 255, 0), thickness=2)
    return src_im


def transform(data, ops=None):
    """ transform """
    if ops is None:
        ops = []
    for op in ops:
        data = op(data)
        if data is None:
            return None
    return data


class TextDetector(object):
    def __init__(self, box_thresh=0.6, unclip_ratio=1.6, det_model_path=None, ort_providers=None):
        if ort_providers is None:
            ort_providers = ['CPUExecutionProvider']
        self.det_algorithm = 'DB'
        self.box_thresh = box_thresh
        self.unclip_ratio = unclip_ratio

        self.preprocess_op = preprocess_op
        self.postprocess_op = DBPostProcess(thresh=0.3, max_candidates=1000, use_dilation=True)
        model_data = get_model_data(model_file) if det_model_path is None else get_model_data_from_path(det_model_path)
        so = ort.SessionOptions()
        so.log_severity_level = 3
        sess = ort.InferenceSession(model_data, so, providers=ort_providers)
        self.output_tensors = None
        self.predictor, self.input_tensor = sess, sess.get_inputs()[0]

    def order_points_clockwise(self, pts):
        """
        reference from: https://github.com/jrosebr1/imutils/blob/master/imutils/perspective.py
        # sort the points based on their x-coordinates
        """
        xSorted = pts[np.argsort(pts[:, 0]), :]

        # grab the left-most and right-most points from the sorted
        # x-roodinate points
        leftMost = xSorted[:2, :]
        rightMost = xSorted[2:, :]

        # now, sort the left-most coordinates according to their
        # y-coordinates so we can grab the top-left and bottom-left
        # points, respectively
        leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
        (tl, bl) = leftMost

        rightMost = rightMost[np.argsort(rightMost[:, 1]), :]
        (tr, br) = rightMost

        rect = np.array([tl, tr, br, bl], dtype="float32")
        return rect

    def clip_det_res(self, points, img_height, img_width):
        for pno in range(points.shape[0]):
            points[pno, 0] = int(min(max(points[pno, 0], 0), img_width - 1))
            points[pno, 1] = int(min(max(points[pno, 1], 0), img_height - 1))
        return points

    def filter_tag_det_res(self, dt_boxes, image_shape):
        img_height, img_width = image_shape[0:2]
        dt_boxes_new = []
        for box in dt_boxes:
            box = self.order_points_clockwise(box)
            box = self.clip_det_res(box, img_height, img_width)
            rect_width = int(np.linalg.norm(box[0] - box[1]))
            rect_height = int(np.linalg.norm(box[0] - box[3]))
            if rect_width <= 3 or rect_height <= 3:
                continue
            dt_boxes_new.append(box)
        dt_boxes = np.array(dt_boxes_new)
        return dt_boxes

    def filter_tag_det_res_only_clip(self, dt_boxes, image_shape):
        img_height, img_width = image_shape[0:2]
        dt_boxes_new = []
        for box in dt_boxes:
            box = self.clip_det_res(box, img_height, img_width)
            dt_boxes_new.append(box)
        dt_boxes = np.array(dt_boxes_new)
        return dt_boxes

    def __call__(self, img, unclip_ratio=None, box_thresh=None):
        if unclip_ratio is None:
            unclip_ratio = self.unclip_ratio
        if box_thresh is None:
            box_thresh = self.box_thresh
        ori_im = img.copy()
        data = {'image': img}
        data = transform(data, self.preprocess_op)
        img, shape_list = data
        if img is None:
            return None, 0
        img = np.expand_dims(img, axis=0)
        shape_list = np.expand_dims(shape_list, axis=0)
        img = img.copy()
        starttime = time.time()

        input_dict = {}
        input_dict[self.input_tensor.name] = img

        outputs = self.predictor.run(self.output_tensors, input_dict)

        preds = {}
        if self.det_algorithm == "EAST":
            preds['f_geo'] = outputs[0]
            preds['f_score'] = outputs[1]
        elif self.det_algorithm == 'SAST':
            preds['f_border'] = outputs[0]
            preds['f_score'] = outputs[1]
            preds['f_tco'] = outputs[2]
            preds['f_tvo'] = outputs[3]
        elif self.det_algorithm == 'DB':
            preds['maps'] = outputs[0]
        else:
            raise NotImplementedError

        post_result = self.postprocess_op(preds, shape_list, unclip_ratio, box_thresh)
        dt_boxes = post_result[0]['points']
        dt_boxes = self.filter_tag_det_res(dt_boxes, ori_im.shape)
        elapse = time.time() - starttime
        return dt_boxes, elapse
