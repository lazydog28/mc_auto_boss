# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: yolo.py
@time: 2024/6/6 上午12:14
@author SuperLazyDog
"""
from constant import root_path
import onnxruntime as rt
import os
import numpy as np
import cv2

model_path = os.path.join(root_path, "models/yolo.onnx")
model = rt.InferenceSession(model_path)
input_name = model.get_inputs()[0].name
label_name = model.get_outputs()[0].name


class LetterBox:
    """
    Resize image and padding for detection, instance segmentation, pose.
    """

    def __init__(
            self,
            new_shape=(640, 640),
            auto=False,
            scaleFill=False,
            scaleup=True,
            center=True,
            stride=32,
    ):
        """初始化LetterBox对象，指定特定参数。

        参数:
            new_shape(tuple): 指定输出图像的新尺寸，默认为(640, 640)。
            auto(bool): 是否自动调整图像尺寸，默认为False。
            scaleFill(bool): 是否根据新尺寸缩放填充图像，默认为False。
            scaleup(bool): 是否允许图像尺寸放大，默认为True。
            center(bool): 是否将图像居中，默认为True。
            stride(int): 步长，默认为32。
        """
        self.new_shape = new_shape
        self.auto = auto
        self.scaleFill = scaleFill
        self.scaleup = scaleup
        self.stride = stride
        self.center = center  # 是否将图像放在中间或左上角

    def __call__(self, labels=None, image=None):
        """对输入的labels和image添加边框，并返回更新后的labels和image。

        Args:
            labels (dict, optional): 输入的标签信息，包括img和其他相关信息，默认为None.
            image (ndarray, optional): 输入的图像，默认为None.

        Returns:
            dict or ndarray: 更新后的labels或image.

        """
        if labels is None:
            labels = {}

        img = labels.get("img") if image is None else image
        shape = img.shape[:2]  # 当前形状 [高度, 宽度]
        new_shape = labels.pop("rect_shape", self.new_shape)
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)

        # 缩放比例 (新 / 旧)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        if not self.scaleup:  # 仅缩小，不放大 (以获得更好的验证mAP)
            r = min(r, 1.0)

        # 计算填充
        ratio = r, r  # 宽度，高度比例
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = (
            new_shape[1] - new_unpad[0],
            new_shape[0] - new_unpad[1],
        )  # 填充的宽度，高度
        if self.auto:  # 最小矩形
            dw, dh = np.mod(dw, self.stride), np.mod(
                dh, self.stride
            )  # 填充的宽度，高度
        elif self.scaleFill:  # 拉伸
            dw, dh = 0.0, 0.0
            new_unpad = (new_shape[1], new_shape[0])
            ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # 宽度，高度比例

        if self.center:
            dw /= 2  # 将填充分为两侧
            dh /= 2

        if shape[::-1] != new_unpad:  # 调整大小
            img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)) if self.center else 0, int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)) if self.center else 0, int(round(dw + 0.1))
        img = cv2.copyMakeBorder(
            img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114)
        )  # 添加边框
        if labels.get("ratio_pad"):
            labels["ratio_pad"] = (labels["ratio_pad"], (left, top))  # 用于评估

        if len(labels):
            labels = self._update_labels(labels, ratio, dw, dh)
            labels["img"] = img
            labels["resized_shape"] = new_shape
            return labels
        else:
            return img

    def _update_labels(self, labels, ratio, padw, padh):
        """Update labels."""
        labels["instances"].convert_bbox(format="xyxy")
        labels["instances"].denormalize(*labels["img"].shape[:2][::-1])
        labels["instances"].scale(*ratio)
        labels["instances"].add_padding(padw, padh)
        return labels


def getInter(box1, box2):
    box1_x1, box1_y1, box1_x2, box1_y2 = (
        box1[0] - box1[2] / 2,
        box1[1] - box1[3] / 2,
        box1[0] + box1[2] / 2,
        box1[1] + box1[3] / 2,
    )
    box2_x1, box2_y1, box2_x2, box2_y2 = (
        box2[0] - box2[2] / 2,
        box2[1] - box1[3] / 2,
        box2[0] + box2[2] / 2,
        box2[1] + box2[3] / 2,
    )
    if box1_x1 > box2_x2 or box1_x2 < box2_x1:
        return 0
    if box1_y1 > box2_y2 or box1_y2 < box2_y1:
        return 0
    x_list = [box1_x1, box1_x2, box2_x1, box2_x2]
    x_list = np.sort(x_list)
    x_inter = x_list[2] - x_list[1]
    y_list = [box1_y1, box1_y2, box2_y1, box2_y2]
    y_list = np.sort(y_list)
    y_inter = y_list[2] - y_list[1]
    inter = x_inter * y_inter
    return inter


def getIou(box1, box2, inter_area):
    box1_area = box1[2] * box1[3]
    box2_area = box2[2] * box2[3]
    union = box1_area + box2_area - inter_area
    iou = inter_area / union
    return iou


def nms(pred, conf_thres, iou_thres):
    conf = pred[..., 4] > conf_thres
    box = pred[conf == True]
    cls_conf = box[..., 5:]
    cls = []
    for i in range(len(cls_conf)):
        cls.append(int(np.argmax(cls_conf[i])))
    total_cls = list(set(cls))
    output_box = []
    for i in range(len(total_cls)):
        clss = total_cls[i]
        cls_box = []
        for j in range(len(cls)):
            if cls[j] == clss:
                box[j][5] = clss
                cls_box.append(box[j][:6])
        cls_box = np.array(cls_box)
        box_conf = cls_box[..., 4]
        box_conf_sort = np.argsort(box_conf)
        max_conf_box = cls_box[box_conf_sort[len(box_conf) - 1]]
        output_box.append(max_conf_box)
        cls_box = np.delete(cls_box, 0, 0)
        while len(cls_box) > 0:
            max_conf_box = output_box[len(output_box) - 1]
            del_index = []
            for j in range(len(cls_box)):
                current_box = cls_box[j]
                interArea = getInter(max_conf_box, current_box)
                iou = getIou(max_conf_box, current_box, interArea)
                if iou > iou_thres:
                    del_index.append(j)
            cls_box = np.delete(cls_box, del_index, 0)
            if len(cls_box) > 0:
                output_box.append(cls_box[0])
                cls_box = np.delete(cls_box, 0, 0)
    return output_box


letterbox = LetterBox((640, 640))


def draw(img, xscale, yscale, pred):
    img_ = img.copy()
    if len(pred):
        for detect in pred:
            detect = [
                int((detect[0] - detect[2] / 2) / xscale),
                int((detect[1] - detect[3] / 2) / yscale),
                int((detect[0] + detect[2] / 2) / xscale),
                int((detect[1] + detect[3] / 2) / yscale),
            ]
            img_ = cv2.rectangle(
                img, (detect[0], detect[1]), (detect[2], detect[3]), (0, 255, 0), 3
            )
    return img_


def search_echoes(img: np.ndarray, conf_thres=0.5, iou_thres=0.5) -> None | int:
    """
    传入 RGB 图像，返回检测到的 echoes 的 x 坐标
    :param img: RGB 图像
    :param conf_thres: 置信度阈值
    :param iou_thres: iou 阈值
    :return:
    """
    x_scale = 640 / img.shape[1]
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # BGR转RGB
    img = np.expand_dims(img, axis=0)  # 增加批次维度
    x = [letterbox(image=x) for x in img]
    im = np.stack(x)
    im = im.transpose((0, 3, 1, 2))  # BHWC转BCHW，(n, 3, h, w)
    im = np.ascontiguousarray(im).astype(np.float32)  # 连续
    im = im / 255  # 归一化
    pred = model.run([label_name], {input_name: im})
    pred = np.transpose(np.squeeze(pred), (1, 0))  # 转置
    pred = pred[np.argsort(pred[..., 4])]  # 按置信度排序
    pred_class = pred[..., 4:]  # 类别置信度
    pred_conf = np.max(pred_class, axis=-1)  # get max conf
    pred = np.insert(pred, 4, pred_conf, axis=-1)  # insert conf to pred
    results = nms(pred, conf_thres, iou_thres)
    # 输出 类别 置信度 坐标
    for result in results:
        cls = int(result[5])
        if cls == 0:
            return int(result[0] / x_scale)
    return None
