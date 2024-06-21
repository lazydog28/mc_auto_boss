# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: echo.py
@time: 2024/6/20 下午9:53
@author RoseRin0
"""
import time

from . import *
import sys

pages = []


def bag(positions: dict[str, Position]) -> bool:
    """
    提示
    :param positions:
    :return:
    """
    if lock_echo() is False:
        print("声骸锁定功能结束或异常退出，结束脚本")
        sys.exit(0)
    return True

bag_page = Page(
    name="声骸",
    targetTexts=[
        TextMatch(
            name="声",
            text="声",
        ),
        TextMatch(
            name="顺序",
            text="顺序",
        ),
        TextMatch(
            name="培养",
            text="培养",
        ),
        TextMatch(
            name="COST",
            text="COST"
        ),
    ],
    action=bag,
)

pages.append(bag_page)
