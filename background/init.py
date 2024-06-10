# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: check.py
@time: 2024/6/3 下午3:57
@author SuperLazyDog
"""
import os
import ctypes
from status import logger
from constant import w, h, scale_factor, real_w, real_h, root_path, hwnd, wait_exit
import win32gui
from multiprocessing import current_process


# 判断当前是否为管理员权限
def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0


if not is_admin():
    print("请以管理员权限运行此程序")
    wait_exit()

if current_process().name == "task":
    logger("开源代码仓库地址：https://github.com/lazydog28/mc_auto_boss")
    logger("初始化中")
    logger(f"窗口大小：{w}x{h} 当前屏幕缩放：{scale_factor} 游戏分辨率：{real_w}x{real_h}")
    logger(f"项目路径：{root_path}")
    logger(f"将窗口移动至左上角")
    rect = win32gui.GetWindowRect(hwnd)  # 获取窗口区域
    win32gui.MoveWindow(
        hwnd, 0, 0, rect[2] - rect[0], rect[3] - rect[1], True
    )  # 设置窗口位置为0,0
