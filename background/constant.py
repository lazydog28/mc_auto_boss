# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: constant.py
@time: 2024/6/5 上午8:24
@author SuperLazyDog
"""
import win32gui
import sys
from ctypes import windll
import os
import re


def get_scale_factor():
    try:
        windll.shcore.SetProcessDpiAwareness(1)  # 设置进程的 DPI 感知
        scale_factor = windll.shcore.GetScaleFactorForDevice(
            0
        )  # 获取主显示器的缩放因子
        return scale_factor / 100  # 返回百分比形式的缩放因子
    except Exception as e:
        print("Error:", e)
        return None


def wait_exit():
    input("按任意键退出...")
    sys.exit(0)


hwnd = win32gui.FindWindow("UnrealWindow", "鸣潮  ")
if hwnd == 0:
    print("未找到游戏窗口")
    wait_exit()
left, top, right, bot = win32gui.GetClientRect(hwnd)
w = right - left
h = bot - top
scale_factor = get_scale_factor()
width_ratio = w / 1920 * scale_factor
height_ratio = h / 1080 * scale_factor
real_w = int(w * scale_factor)
real_h = int(h * scale_factor)
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 判断 root_path 中是否包含中文或特殊字符
special_chars_pattern = r"[\u4e00-\u9fa5\!\@\#\$\%\^\&\*\(\)]"
if bool(re.search(special_chars_pattern, root_path)):
    print("请将项目路径移动到纯英文路径下")
    wait_exit()
