# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: echo.py
@time: 2024/6/20 下午9:53
@author RoseRin0
"""
from . import *
import sys

pages = []


def echo_bag(positions: dict[str, Position]) -> bool:
    """
    提示
    :param positions:
    :return:
    """
    info.bagIsOpen = True
    control.activate()
    time.sleep(0.2)
    if echo_bag_lock() is False:
        logger("背包声骸锁定功能结束")
        time.sleep(1)
        control.tap("b")
        logger("已返回大世界")
        time.sleep(1)
        sys.exit(0)
    return True


echo_bag_page = Page(
    name="声骸",
    targetTexts=[
        TextMatch(
            name="声",
            text="声",
        ),
        TextMatch(
            name="培养",
            text="培养",
        ),
    ],
    action=echo_bag,
)

pages.append(echo_bag_page)


def terminal_action(positions: dict[str, Position]) -> bool:
    """
    提示
    :param positions:
    :return:
    """
    control.esc()
    time.sleep(2)
    return True


terminal_page = Page(
    name="终端",
    targetTexts=[
        TextMatch(
            name="终端",
            text="终端",
        ),
    ],
    action=terminal_action,
)

pages.append(terminal_page)


