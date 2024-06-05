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


# 战斗完成 前进吸收
def judgment_forward() -> bool:
    return (datetime.now() - info.lastFightTime).seconds > config.MaxIdleTime / 2


def judgment_forward_action():
    return forward()


judgment_forward_conditional_action = ConditionalAction(
    name="前进",
    condition=judgment_forward, action=judgment_forward_action
)
conditional_actions.append(judgment_forward_conditional_action)


# 超过最大空闲时间
def judgment_idle() -> bool:
    return (datetime.now() - info.lastFightTime).seconds > config.MaxIdleTime


def judgment_idle_action() -> bool:
    info.status = Status.idle
    info.lastFightTime = datetime.now()
    return transfer_boss()


judgment_idle_conditional_action = ConditionalAction(
    name="超过最大空闲时间,前往boss",
    condition=judgment_idle, action=judgment_idle_action
)
conditional_actions.append(judgment_idle_conditional_action)


# 超过最大战斗时间
def judgment_fight() -> bool:
    return (datetime.now() - info.fightTime).seconds > config.MaxFightTime


def judgment_fight_action() -> bool:
    info.status = Status.idle
    info.fightTime = datetime.now()
    return transfer_boss()


judgment_fight_conditional_action = ConditionalAction(
    name="超过最大战斗时间,前往boss",
    condition=judgment_fight, action=judgment_fight_action
)

conditional_actions.append(judgment_fight_conditional_action)
