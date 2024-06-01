# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: operation.py
@time: 2024/5/26 下午9:17
@author SuperLazyDog
"""
import time
import numpy as np
from utils import (
    screenshot,
    matchTemplate,
    search_text,
    ocr,
    hwnd,
    width_ratio,
    height_ratio,
    root_path,
)
from PIL import Image
from control import Control
import os

select_role_index = 1
control = Control(hwnd)


def interactive():
    control.tap("f")


last_select_role_time = time.time()


def click_position(position: list[list[int]]):
    """
    [[       1135,         282],
       [       1445,         282],
       [       1445,         306],
       [       1135,         306]]
    :param position:
    :return:
    """
    # 分析position的中点
    x = 0
    y = 0
    for i in range(4):
        x += position[i][0]
        y += position[i][1]
    x = x // 4
    y = y // 4
    control.click(x, y)


def select_role():
    global last_select_role_time, select_role_index
    if time.time() - last_select_role_time < 2:
        return
    last_select_role_time = time.time()
    select_role_index += 1
    if select_role_index > 3:
        select_role_index = 1
    control.tap(str(select_role_index))


def release_skills():
    select_role()
    control.mouse_middle()
    control.tap("e")
    control.tap("q")
    control.tap("r")
    for i in range(5):
        control.click()
        time.sleep(0.1)


def leaving_battle():
    for i in range(3):
        interactive()
        time.sleep(1)
    control.esc()
    time.sleep(1)


def forward():
    control.key_press("w")
    time.sleep(0.1)
    control.key_release("w")


def transfer_beacon():
    """
    传送信标
    :return:
    """
    control.activate()
    control.tap("m")
    time.sleep(1)
    for i in range(20):
        control.click(1810 * width_ratio, 315 * height_ratio)
    img = screenshot()
    template = Image.open(os.path.join(root_path, r"template\借位信标.png"))
    template = np.array(template)
    coordinate = matchTemplate(img, template)
    print("coordinate", coordinate)
    if not coordinate:
        control.esc()
        return None
    control.click(coordinate.get("x"), coordinate.get("y"))
    time.sleep(1)
    img = screenshot()
    result = ocr(img)
    text_info = search_text(result, "借位信标")
    if not text_info:
        control.esc()
        return None
    click_position(text_info.get("position"))
    time.sleep(1)
    control.click(1745 * width_ratio, 1000 * height_ratio)


def mouse_scroll():
    control.scroll(1)
    time.sleep(1)


def select_levels():
    control.mouse_press(320 * width_ratio, 185 * height_ratio)
    time.sleep(1)
    control.mouse_release(320 * width_ratio, 185 * height_ratio)
    time.sleep(1)
    control.click(1500 * width_ratio, 1000 * height_ratio)
    time.sleep(1)
