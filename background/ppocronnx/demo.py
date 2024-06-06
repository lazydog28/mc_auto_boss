from ppocronnx.predict_system import TextSystem
import cv2
import logging
import sys
from PIL import Image
from ppocronnx.utility import draw_ocr_box_result


def main():
    text_sys = TextSystem()
    print(text_sys.ocr_single_line(cv2.imread('test3.png')))
    img = cv2.imread('test.png')
    img = cv2.resize(img, (0, 0), fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)
    res = text_sys.detect_and_ocr(img, box_thresh=0.5, unclip_ratio=2)
    for boxed_result in res:
        print("{}, {:.3f}".format(boxed_result.ocr_text, boxed_result.score))

    draw_img = draw_ocr_box_result(img, res, 0.5, 'WeiRuanYaHei-1.ttf')
    cv2.imshow('test', draw_img)
    cv2.waitKey()


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()
