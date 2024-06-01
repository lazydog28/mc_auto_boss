# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: utils.py
@time: 2024/5/26 下午8:59
@author SuperLazyDog
"""
from typing import List, Dict, Any
from PyQt5.QtGui import QPixmap
import numpy as np
from PIL import Image
from PyQt5.QtWidgets import QApplication
import sys
import cv2
from paddleocr import PaddleOCR
from datetime import datetime

print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 初始化中")

app = QApplication(sys.argv)

cand_alphabet_list = [
    "吸收",
    "进入",
    "推荐等级",
    "开启挑战",
    "击败",
    "确认",
    "取消",
    "离开",
    "领取",
    "借位信标",
    "回收",
    "快速旅行",
    "领取奖励",
    "终端",
]
cand_alphabet = "".join(cand_alphabet_list)

ocrIns = PaddleOCR(lang="ch", use_gpu=True, show_log=False)


def screenshot() -> np.ndarray:
    screen = QApplication.primaryScreen()
    img = screen.grabWindow(0)
    img = _screenshot_to_numpy(img)
    return img


def ocr(img: np.ndarray) -> List[Dict[str, Any]]:
    results = ocrIns.ocr(img, cls=False)
    if len(results) == 0:
        return []
    results = results[0]
    if results is None:
        return []
    res = []
    for result in results:
        text = [char for char in result[1][0] if char in cand_alphabet]
        text = "".join(text)
        if len(text) == 0:
            continue
        position = result[0]
        res.append({"text": text, "position": position})
    return res


def ocr_zh(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    将ocr识别结果中的非中文字符去除
    :param results:
    :return:
    """
    for item in results:
        text = item.get("text")
        newText = ""
        for char in text:
            if "\u4e00" <= char <= "\u9fa5":
                newText += char
        item["text"] = newText
    return results


def _screenshot_to_numpy(qImage: QPixmap) -> np.ndarray:
    """
    将QPixmap转换为numpy数组
    :param qImage:  QPixmap
    :return: np.ndarray
    """
    qImage = qImage.toImage()
    qImage = qImage.convertToFormat(4)
    width = qImage.width()
    height = qImage.height()
    ptr = qImage.bits()
    ptr.setsize(qImage.byteCount())
    arr = np.array(ptr).reshape(height, width, 4)  # 4 for ARGB channels
    return arr


def _screenshot_to_pil(qImage: QPixmap) -> Image.Image:
    """
    将QPixmap转换为PIL Image
    :param qImage:  QPixmap
    :return:  Image.Image
    """
    buffer = qImage.bits().asstring(qImage.byteCount())
    image = Image.frombytes(
        "RGBA", (qImage.width(), qImage.height()), buffer, "raw", "BGRA"
    )
    return image


def matchTemplate(
        img: np.ndarray, template: np.ndarray, threshold: float = 0.8
) -> None | Dict[str, Any]:
    """
    使用 opencv matchTemplate 方法 模板匹配 返回匹配结果
    :param img:  大图片
    :param template: 小图片
    :param threshold:  阈值
    :return:
    """
    # 判断是否为灰度图，如果不是转换为灰度图
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if len(template.shape) == 3:
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    # confidence = np.max(res)
    # print(confidence)
    loc = np.where(res >= threshold)
    if len(loc[0]) == 0:
        return None
    else:
        # 选择最大值
        confidence = np.max(res)
        maxLoc = np.where(res == confidence)
        return {
            "x": maxLoc[1][0] + template.shape[1] // 2,
            "y": maxLoc[0][0] + template.shape[0] // 2,
            "w": template.shape[1],
            "h": template.shape[0],
            "confidence": confidence,
        }


def search_text(results: List[Dict[str, Any]], target: str):
    for result in results:
        if target in result.get("text"):
            return result
    return None
