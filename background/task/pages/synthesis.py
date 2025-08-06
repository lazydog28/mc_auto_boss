# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: synthesis.py
@time: 2024/6/8 下午10:08
@author SuperLazyDog
"""
import sys
import time

from . import *

pages = []


def automatically_placed_in(positions: dict[str, Position]) -> bool:
    """
    自动放入
    :param positions:
    :return:
    """
    control.activate()
    click_position(positions.get("自动放入"))
    time.sleep(0.5)
    return True


automatically_placed_in_page = Page(
    name="自动放入",
    targetTexts=[
        TextMatch(
            name="自动放入",
            text="自动放入",
        ),
    ],
    action=automatically_placed_in,
)

pages.append(automatically_placed_in_page)


def fusion(positions: dict[str, Position]) -> bool:
    """
    数据融合
    :param positions:
    :return:
    """
    control.activate()
    click_position(positions.get("数据融合"))
    time.sleep(1)
    return True


fusion_page = Page(
    name="数据融合",
    targetTexts=[
        TextMatch(
            name="数据融合",
            text="数据融合",
            position=Position(
                x1=480,
            )
        ),
    ],
    excludeTexts=[
        TextMatch(
            name="自动放入",
            text="自动放入",
        ),
    ],
    action=fusion,
)
pages.append(fusion_page)


def tips(positions: dict[str, Position]) -> bool:
    """
    提示
    :param positions:
    :return:
    """
    control.activate()
    click_position(positions.get("登录"))
    time.sleep(1)
    click_position(positions.get("确认"))
    time.sleep(1)
    return True


tips_page = Page(
    name="提示",
    targetTexts=[
        TextMatch(
            name="提示",
            text="提示",
        ),
        TextMatch(
            name="确认",
            text=template("^确认$"),
        ),
        TextMatch(
            name="登录",
            text="登录",
        ),
    ],
    action=tips,
)

pages.append(tips_page)


def get_echoes(positions: dict[str, Position]) -> bool:
    """
    获取回音
    :param positions:
    :return:
    """
    control.activate()
    echo_synthesis()
    time.sleep(1)
    return True


get_echoes_page = Page(
    name="获得声骸",
    targetTexts=[
        TextMatch(
            name="获得声",
            text="获得声",
        ),
    ],
    action=get_echoes,
)

pages.append(get_echoes_page)


def echo_not_enough_action(positions: dict[str, Position]) -> bool:
    """
    获取回音
    :param positions:
    :return:
    """
    logger("合成结束")
    info.dataMergeFinish = True
    return True


echo_not_enough_page = Page(
    name="材料不足",
    targetTexts=[
        TextMatch(
            name="材料不足",
            text="材料不足",
        ),
    ],
    action=echo_not_enough_action,
)

pages.append(echo_not_enough_page)


def terminal_action(positions: dict[str, Position]) -> bool:
    """
    获取回音
    :param positions:
    :return:
    """
    control.activate()
    click_position(positions.get("数据坞"))
    info.needOpenDataMerge = False
    time.sleep(1)
    return True


terminal_page = Page(
    name="终端",
    targetTexts=[
        TextMatch(
            name="唤取|共鸣者|教程百科",
            text=re.compile(r"(唤取|共鸣者|教程百科)"),
        ),
        TextMatch(
            name="数据坞",
            text="数据坞",
        ),

    ],
    action=terminal_action,
)

pages.append(terminal_page)


def data_bank_action(positions: dict[str, Position]) -> bool:
    """
    获取回音
    :param positions:
    :return:
    """
    synthesis_data_bank_action()
    time.sleep(1)
    return True


data_bank_page = Page(
    name="数据坞",
    targetTexts=[
        TextMatch(
            name="数据坞信息",
            text="数据坞信息",
        ),

    ],
    action=data_bank_action,
)

pages.append(data_bank_page)

