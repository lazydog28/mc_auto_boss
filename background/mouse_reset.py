# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: mouse_reset.py
@time: 2024/6/2 下午4:02
@author SuperLazyDog
"""
import time

import win32gui
from pynput.mouse import Controller
import math
from threading import Event

import hwnd_util
from status import logger


def mouse_reset(e: Event):
    logger("鼠标重置进程启动成功")
    mouse = Controller()
    last_position = mouse.position
    hwnd = None
    while True:
        time.sleep(0.01)  # 0.01秒检测一次
        if e.is_set():
            break
        if not hwnd or not win32gui.IsWindow(hwnd):
            time.sleep(0.5)
            try:
                hwnd = hwnd_util.get_mc_hwnd()
            except Exception:
                pass
            continue
        current_position = mouse.position
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        center_position = (left + right) / 2, (top + bottom) / 2
        curr_pos_to_center_distance = math.sqrt(
            (current_position[0] - center_position[0]) ** 2
            + (current_position[1] - center_position[1]) ** 2
        )
        curr_pos_to_last_pos_distance = math.sqrt(
            (current_position[0] - last_position[0]) ** 2
            + (current_position[1] - last_position[1]) ** 2
        )
        if curr_pos_to_last_pos_distance > 200 and curr_pos_to_center_distance < 50:
            mouse.position = last_position
        else:
            last_position = current_position
