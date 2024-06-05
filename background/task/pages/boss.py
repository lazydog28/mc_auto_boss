# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: boss.py
@time: 2024/6/5 上午9:55
@author SuperLazyDog
"""
# 大世界boss脚本
from . import *
pages = []


# 失去意识
def unconscious_action(positions: dict[str, Position]) -> bool:
    """
    失去意识
    :param positions: 位置信息
    :return:
    """
    position = positions.get("复苏")
    click_position(position)
    return True


unconscious_action_page = Page(
    name="失去意识",
    targetTexts=[
        TextMatch(
            name="失去意识",
            text="失去意识",
        ),
        TextMatch(
            name="复苏",
            text="复苏",
        ),
    ],
    action=unconscious_action,
)
pages.append(unconscious_action_page)


# 声弦 交互
def voice_string_interaction_action(positions: dict[str, Position]) -> bool:
    """
    声弦 交互
    :param positions: 位置信息
    :return:
    """
    control.tap("f")
    return True


voice_string_interaction_page = Page(
    name="声弦交互",
    targetTexts=[
        TextMatch(
            name="声弦",
            text="声弦",
        ),
    ],
    action=voice_string_interaction_action,
)

pages.append(voice_string_interaction_page)
