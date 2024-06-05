# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: dreamless.py
@time: 2024/6/5 上午10:23
@author SuperLazyDog
"""
# 无妄者脚本
from . import *


# 进入
def enter_action(positions: dict[str, Position]) -> bool:
    """
    进入
    :param positions: 位置信息
    :return:
    """
    control.tap("f")
    return True


enter_page = Page(
    name="进入",
    targetTexts=[
        TextMatch(
            name="进入",
            text="进入",
        ),
    ],
    excludeTexts=[
        TextMatch(
            name="确认",
            text="确认",
        ),
    ],
    action=enter_action,
)


# 推荐等级
def recommended_level_action(positions: dict[str, Position]) -> bool:
    """
    推荐等级
    :param positions: 位置信息
    :return:
    """
    control.tap("f")
    result = wait_text("推荐等级40")
    if not result:
        control.esc()
        return False
    for i in range(3):
        click_position(result.position)
        time.sleep(1)
    result = find_text("单人挑战")
    if not result:
        control.esc()
        return False
    click_position(result.position)
    time.sleep(1)
