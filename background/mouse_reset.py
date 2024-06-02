# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: mouse_reset.py
@time: 2024/6/2 下午4:02
@author SuperLazyDog
"""
from pynput.mouse import Controller
import math
from datetime import datetime
from multiprocessing import Event
from utils import logger_msg


def mouse_reset(e: Event):
    logger_msg("鼠标重置进程启动成功")
    mouse = Controller()
    last_position = mouse.position
    last_time = datetime.now()
    while True:
        if e.is_set():
            break
        if (datetime.now() - last_time).total_seconds() < 0.01:
            continue
        last_time = datetime.now()
        current_position = mouse.position
        distance = math.sqrt(
            (current_position[0] - last_position[0]) ** 2
            + (current_position[1] - last_position[1]) ** 2
        )
        if distance > 200:
            mouse.position = last_position
        else:
            last_position = current_position
