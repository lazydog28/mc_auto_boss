# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: mouse.py
@time: 2024/5/30 下午9:03
@author SuperLazyDog
"""
import time
import win32gui
import win32con
import win32api


class Control:
    def __init__(self, hwnd: int):
        self.hwnd = hwnd

    def click(self, x: int | float = 0, y: int | float = 0):
        x = x if isinstance(x, int) else int(x)
        y = y if isinstance(y, int) else int(y)
        long_position = win32api.MAKELONG(x, y)
        win32gui.PostMessage(
            self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, long_position
        )  # 鼠标左键按下
        time.sleep(0.2)
        win32gui.PostMessage(
            self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, long_position
        )  # 鼠标左键抬起
        time.sleep(0.1)

    def mouse_middle(self, x: int = 0, y: int = 0):
        x = x if isinstance(x, int) else int(x)
        y = y if isinstance(y, int) else int(y)
        self.activate()
        long_position = win32api.MAKELONG(x, y)  # 生成坐标
        win32gui.PostMessage(
            self.hwnd, win32con.WM_MBUTTONDOWN, win32con.MK_MBUTTON, long_position
        )  # 鼠标中键按下
        win32gui.PostMessage(
            self.hwnd, win32con.WM_MBUTTONUP, win32con.MK_MBUTTON, long_position
        )  # 鼠标中键抬起

    def mouse_press(self, x: int | float = 0, y: int | float = 0):
        x = x if isinstance(x, int) else int(x)
        y = y if isinstance(y, int) else int(y)
        long_position = win32api.MAKELONG(x, y)
        win32gui.PostMessage(
            self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, long_position
        )

    def mouse_release(self, x: int | float = 0, y: int | float = 0):
        x = x if isinstance(x, int) else int(x)
        y = y if isinstance(y, int) else int(y)
        long_position = win32api.MAKELONG(x, y)
        win32gui.PostMessage(
            self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, long_position
        )

    def scroll(self, count: int, x: int | float = 0, y: int | float = 0):
        count = count if isinstance(count, int) else int(count)
        x = x if isinstance(x, int) else int(x)
        y = y if isinstance(y, int) else int(y)
        lParam = win32api.MAKELONG(x, y)
        wParam = win32api.MAKELONG(0, win32con.WHEEL_DELTA * count)
        win32gui.SendMessage(self.hwnd, win32con.WM_MOUSEWHEEL, wParam, lParam)

    def tap(self, key: str | int):
        if isinstance(key, str):
            key = ord(key.upper())
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYDOWN, key, 0)
        time.sleep(0.1) # 按键时间 不确定是否需要
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, key, 0)

    def esc(self):
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYDOWN, win32con.VK_ESCAPE, 0)
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, win32con.VK_ESCAPE, 0)

    def key_press(self, key: int | str):
        if isinstance(key, str):
            key = ord(key.upper())
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYDOWN, key, 0)

    def key_release(self, key: int | str):
        if isinstance(key, str):
            key = ord(key.upper())
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, key, 0)

    def alt_press(self):
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYDOWN, win32con.VK_MENU, 0)

    def alt_release(self):
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, win32con.VK_MENU, 0)

    def activate(self):
        win32gui.PostMessage(self.hwnd, win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)

    def inactivate(self):
        win32gui.PostMessage(self.hwnd, win32con.WM_ACTIVATE, win32con.WA_INACTIVE, 0)

    def space(self):
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYDOWN, win32con.VK_SPACE, 0)
        win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, win32con.VK_SPACE, 0)

    def move_to(self, x: int | float, y: int | float):
        x = x if isinstance(x, int) else int(x)
        y = y if isinstance(y, int) else int(y)
        lParam = win32api.MAKELONG(x, y)
        win32gui.PostMessage(self.hwnd, win32con.WM_MOUSEMOVE, 0, lParam)
