# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: boss.py
@time: 2024/6/5 下午1:46
@author SuperLazyDog
"""
import time

from status import Status, logger
from schema import ConditionalAction
from . import *

conditional_actions = []


def judgment_absorption_action():
    if info.fightEndFlag:
        absorption_max_time = (
            config.MaxEchoAbsorptionTime if config.MaxEchoAbsorptionTime > 5 else 5
        )
        if (datetime.now() - info.fightEndTime).seconds < absorption_max_time:
            info.echoSearchTimesCount += 1
            if info.echoSearchTimesCount == 1:
                info.echoSearchStartTime = datetime.now()
                info.searchTimes = 0
            if config.SearchEchoes:
                absorption_action()
            else:
                forward()
        else:
            info.needAbsorption = False


# 战斗完成 吸收
def judgment_absorption() -> bool:
    return (
        (datetime.now() - info.lastFightTime).seconds
        < config.MaxEchoAbsorptionTime + 5  # 给5秒去判断是否超时，设置吸收Flag为False，否则有概率卡在吸收
        and info.needAbsorption  # 未吸收
        and info.status != Status.fight
    )


def add_judgment_absorption_condition_action():
    judgment_absorption_condition_action = ConditionalAction(
        name="搜索声骸", condition=judgment_absorption, action=judgment_absorption_action
    )
    conditional_actions.append(judgment_absorption_condition_action)


# 超过最大空闲时间
def judgment_idle() -> bool:
    return (
        datetime.now() - info.lastFightTime
    ).seconds > config.MaxIdleTime and not info.inDreamless and not info.inJue


def judgment_idle_action() -> bool:
    info.status = Status.idle
    if not info.inGame:
        logger("正在确认游戏状态...", "WARN")
        if check_in_animation(in_game=True) == "is available":
            logger("已成功进入游戏", "WARN")
            check_game_restarting(del_file=True)
            time.sleep(1)
    if check_game_restarting():
        logger("等待游戏重启中...", "WARN")
        time.sleep(3)
        return False
    if not info.inGame:
        logger("未确认到游戏状态，重试", "WARN")
        time.sleep(1)
    return transfer()


def add_judgment_idle_conditional_action():
    judgment_idle_conditional_action = ConditionalAction(
        name="超过最大空闲时间,前往boss",
        condition=judgment_idle,
        action=judgment_idle_action,
    )
    conditional_actions.append(judgment_idle_conditional_action)


# 超过最大战斗时间
def judgment_fight() -> bool:
    return (
        datetime.now() - info.fightTime
    ).seconds > config.MaxFightTime and not info.inDreamless and not info.inJue


def judgment_fight_action() -> bool:
    info.status = Status.idle
    info.fightTime = datetime.now()
    return transfer()


def add_judgment_fight_conditional_action():
    judgment_fight_conditional_action = ConditionalAction(
        name="超过最大战斗时间,前往boss",
        condition=judgment_fight,
        action=judgment_fight_action,
    )
    conditional_actions.append(judgment_fight_conditional_action)


# def judgment_leave() -> bool:
#     return (
#             datetime.now() - info.lastFightTime
#     ).seconds > config.MaxIdleTime and (info.inDreamless or info.inJue)
#
#
# def judgment_leave_action() -> bool:
#     # 重置最后战斗时间
#     if info.needAbsorption and config.SearchDreamlessEchoes:
#         absorption_action()
#     else:
#         absorption_and_receive_rewards({})
#     control.esc()
#     time.sleep(1)
#     info.lastFightTime = datetime.now()
#     return True
#
#
# def add_judgment_leave_conditional_action():
#     judgment_leave_conditional_action = ConditionalAction(
#         name="副本内超过最大空闲时间,离开",
#         condition=judgment_leave,
#         action=judgment_leave_action,
#     )
#     conditional_actions.append(judgment_leave_conditional_action)


add_judgment_absorption_condition_action()  # 搜索声骸
add_judgment_idle_conditional_action()  # 超过最大空闲时间
add_judgment_fight_conditional_action()  # 超过最大战斗时间
# add_judgment_leave_conditional_action()  # 副本内超过最大战斗时间
