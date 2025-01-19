# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: boss.py
@time: 2024/6/5 下午1:46
@author SuperLazyDog
"""
import time

from status import Status
from schema import ConditionalAction
from . import *

conditional_actions = []


def judgment_absorption_action():
    if config.SearchEchoes:
        absorption_action()
    else:
        forward()
    if config.CharacterHeal:
        check_heal()
    return True


# 战斗完成 等待搜索声骸 吸收
def judgment_absorption() -> bool:
    time.sleep(0.1)
    return (
            config.MaxIdleTime / 2
            < (datetime.now() - info.lastFightTime).seconds
            < config.MaxIdleTime  # 空闲时间未超过最大空闲时间 且 空闲时间超过最大空闲时间的一半
            and info.needAbsorption  # 未吸收
    )


judgment_absorption_condition_action = ConditionalAction(
    name="搜索声骸", condition=judgment_absorption, action=judgment_absorption_action
)
conditional_actions.append(judgment_absorption_condition_action)


# 超过最大空闲时间
def judgment_idle() -> bool:
    time.sleep(0.1)
    return (
            datetime.now() - info.lastFightTime
    ).seconds > config.MaxIdleTime and not info.inDreamless and not info.inJue and not info.inHecate


def judgment_idle_action() -> bool:
    info.status = Status.idle
    return transfer()


judgment_idle_conditional_action = ConditionalAction(
    name="超过最大空闲时间,前往boss",
    condition=judgment_idle,
    action=judgment_idle_action,
)
conditional_actions.append(judgment_idle_conditional_action)


# 超过最大战斗时间
def judgment_fight() -> bool:
    time.sleep(0.1)
    return (
            datetime.now() - info.fightTime
    ).seconds > config.MaxFightTime and not info.inDreamless and not info.inJue and not info.inHecate


def judgment_fight_action() -> bool:
    info.status = Status.idle
    info.fightTime = datetime.now()
    return transfer()


judgment_fight_conditional_action = ConditionalAction(
    name="超过最大战斗时间,前往boss",
    condition=judgment_fight,
    action=judgment_fight_action,
)

conditional_actions.append(judgment_fight_conditional_action)


def judgment_leave() -> bool:
    time.sleep(0.1)
    return (
            datetime.now() - info.lastFightTime
    ).seconds > config.MaxIdleTime and (info.inDreamless or info.inJue or info.inHecate)


def judgment_leave_action() -> bool:
    # 重置最后战斗时间
    if info.needAbsorption and config.SearchDreamlessEchoes:
        absorption_action()
    else:
        absorption_and_receive_rewards({})
    if config.CharacterHeal:
        check_heal()
    control.esc()
    time.sleep(1)
    info.lastFightTime = datetime.now()
    return True


judgment_leave_conditional_action = ConditionalAction(
    name="副本内超过最大空闲时间,离开",
    condition=judgment_leave,
    action=judgment_leave_action,
)
conditional_actions.append(judgment_leave_conditional_action)
