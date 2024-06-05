# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: general.py
@time: 2024/6/5 上午9:34
@author SuperLazyDog
"""
import time

from . import *

pages = []


# 吸收声骸
def absorption_action(positions: dict[str, Position]) -> bool:
    """
    吸收声骸
    :param positions: 位置信息
    :return:
    """
    info.absorptionCount += 1
    interactive()
    time.sleep(1)
    info.needAbsorption = False
    return True


absorption_page = Page(
    name="吸收",
    targetTexts=[
        TextMatch(
            name="吸收",
            text="吸收",
        ),
    ],
    action=absorption_action,
)

pages.append(absorption_page)


# 选择复苏物品
def select_recovery_items(positions: dict[str, Position]) -> bool:
    """
    取消选择复苏物品
    :param positions:
    :return:
    """
    control.esc()
    return True


select_recovery_items_page = Page(
    name="选择复苏物品",
    targetTexts=[
        TextMatch(
            name="选择复苏物品",
            text="选择复苏物品",
        ),
    ],
    action=select_recovery_items,
)
pages.append(select_recovery_items_page)


# 退出副本
def exit_instance(positions: dict[str, Position]) -> bool:
    """
    退出副本
    :param positions:
    :return:
    """
    position = positions.get("退出副本", None)
    if position is None:
        return False
    click_position(position)
    return True


exit_instance_page = Page(
    name="退出副本",
    targetTexts=[
        TextMatch(
            name="退出副本",
            text="退出副本",
        ),
    ],
    action=exit_instance,
)

pages.append(exit_instance_page)


# 终端
def terminal_action(positions: dict[str, Position]) -> bool:
    """
    终端
    :param positions: 位置信息
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


# 击败 战斗状态
def fight_action(positions: dict[str, Position]) -> bool:
    """
    击败 战斗状态
    :param positions: 位置信息
    :return:
    """
    release_skills()
    now = datetime.now()
    if info.status != Status.fight:
        info.fightCount += 1
        info.needAbsorption = True
        info.fightTime = now
    info.status = Status.fight
    info.lastFightTime = now
    return True


fight_page = Page(
    name="战斗画面",
    targetTexts=[
        TextMatch(
            name="击败",
            text="击败",
        ),
    ],
    action=fight_action,
)

pages.append(fight_page)


# 点击领取今日月卡奖励
def click_receive_monthly_card_rewards(positions: dict[str, Position]) -> bool:
    """
    点击领取今日月卡奖励
    :param positions: 位置信息
    :return:
    """
    position = positions.get("领取今日月卡奖励", None)
    if position is None:
        return False
    click_position(position)
    return True
