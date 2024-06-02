# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: mouse_reset.py
@time: 2024/6/2 下午4:02
@author SuperLazyDog
"""
from pynput.mouse import Controller
import math
from utils import logger_msg
from datetime import datetime
from threading import Thread, Event

mouse_reset_event = Event()  # 用于停止鼠标重置线程


def mouse_reset(e: Event):
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
            (current_position[0] - last_position[0]) ** 2 + (current_position[1] - last_position[1]) ** 2)
        if distance > 200:
            logger_msg("重置鼠标位置")
            mouse.position = last_position
        else:
            last_position = current_position


mouse_reset_thread = Thread(target=mouse_reset, args=(mouse_reset_event,))
mouse_reset_thread.start()
logger_msg("鼠标重置线程启动")
