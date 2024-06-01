# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: operation.py
@time: 2024/5/26 下午9:17
@author SuperLazyDog
"""
import time
import numpy as np
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyController
from utils import screenshot, matchTemplate, search_text, ocr
from PIL import Image

mouse = MouseController()
keyboard = KeyController()

select_role_index = 1


def interactive():
    keyboard.tap("f")
    time.sleep(0.5)


last_select_role_time = time.time()


def tap(key):
    keyboard.press(key)
    time.sleep(0.1)
    keyboard.release(key)


def mouse_goto(x, y):
    current_x, current_y = mouse.position
    dx = x - current_x
    dy = y - current_y
    mouse.move(dx, dy)


def click(x, y):
    mouse_goto(x, y)
    mouse.press(Button.left)
    time.sleep(0.2)
    mouse.release(Button.left)


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
    click(x, y)


def select_role():
    global last_select_role_time, select_role_index
    if time.time() - last_select_role_time < 2:
        return
    last_select_role_time = time.time()
    select_role_index += 1
    if select_role_index > 3:
        select_role_index = 1
    keyboard.tap(str(select_role_index))


def release_skills():
    select_role()
    mouse.click(Button.middle)
    tap('e')
    tap('q')
    tap('r')
    for i in range(5):
        mouse.press(Button.left)
        time.sleep(0.1)
        mouse.release(Button.left)
        time.sleep(0.1)


def select_levels():
    click(320, 185)
    time.sleep(1)
    click(320, 185)
    time.sleep(1)
    click(1500, 1000)
    mouse.click(Button.left)
    time.sleep(3)


def leaving_battle():
    for i in range(3):
        interactive()
        time.sleep(1)
    keyboard.tap(Key.esc)
    time.sleep(1)


def forward():
    keyboard.press('w')
    time.sleep(0.1)
    keyboard.release('w')


def transfer_beacon():
    """
    传送信标
    :return:
    """
    keyboard.tap("m")
    time.sleep(1)
    for i in range(10):
        click(1810, 315)
    img = screenshot()
    template = Image.open(r"D:\project\python\mc\template\借位信标.png")
    template = np.array(template)
    coordinate = matchTemplate(img, template)
    if not coordinate:
        keyboard.tap(Key.esc)
        return None
    click(coordinate.get("x"), coordinate.get("y"))
    time.sleep(1)
    img = screenshot()
    result = ocr(img)
    text_info = search_text(result, "借位信标")
    click_position(text_info.get("position"))
    time.sleep(1)
    click(1745, 1000)


def mouse_scroll():
    mouse.scroll(0, 1000)
    time.sleep(1)
