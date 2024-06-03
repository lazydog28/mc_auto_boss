# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: check.py
@time: 2024/6/3 下午3:57
@author SuperLazyDog
"""
import os
import ctypes


# 判断当前是否为管理员权限
def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0


if not is_admin():
    print("请以管理员权限运行此程序")
    exit()
