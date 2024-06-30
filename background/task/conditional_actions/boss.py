# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: boss.py
@time: 2024/6/5 下午1:46
@author SuperLazyDog
"""

from status import Status
from schema import ConditionalAction
from . import *

conditional_actions = []


def judgment_absorption_action():
    if config.SearchEchoes:
        absorption_action()
    else:
        forward()


# 战斗完成 吸收
def judgment_absorption() -> bool:
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
    return (
        datetime.now() - info.lastFightTime
    ).seconds > config.MaxIdleTime and not info.inDreamless and not info.inJue


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
    return (
        datetime.now() - info.fightTime
    ).seconds > config.MaxFightTime and not info.inDreamless and not info.inJue


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
