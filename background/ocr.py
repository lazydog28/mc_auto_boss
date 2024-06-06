# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: ocr.py
@time: 2024/6/5 下午4:36
@author SuperLazyDog
"""
import time
from ppocronnx import TextSystem
from multiprocessing import current_process
import numpy as np
from schema import OcrResult, Position
from config import config

ocrIns: TextSystem = None

if current_process().name == "task":
    ocrIns = TextSystem()

last_time = time.time()


def ocr(img: np.ndarray) -> list[OcrResult]:
    global last_time
    if config.OcrInterval > 0 and time.time() - last_time < config.OcrInterval:
        if wait_time := config.OcrInterval - (time.time() - last_time) > 0:
            time.sleep(wait_time)
    last_time = time.time()
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
