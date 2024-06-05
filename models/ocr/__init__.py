# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: __init__.py.py
@time: 2024/6/5 上午11:20
@author SuperLazyDog
"""
from .predict_system import TextSystem
from schema import OcrResult, Position
import numpy as np
from multiprocessing import current_process

ocrIns: TextSystem = None

if current_process().name == "task":
    ocrIns = TextSystem()


def ocr(img: np.ndarray) -> list[OcrResult]:
    results = ocrIns.detect_and_ocr(img)
    if len(results) == 0:
        return []
    res = []
    for result in results:
        text = result.ocr_text
        position = result.box
        x1, y1, x2, y2 = position[0][0], position[0][1], position[2][0], position[2][1]
        position = Position(x1=x1, y1=y1, x2=x2, y2=y2)
        confidence = result.score
        res.append(OcrResult(text=text, position=position, confidence=confidence))
    return res
