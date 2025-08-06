# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: echo_bag_lock.py
@time: 2024/6/5 下午1:46
@author wakening
"""
from schema import ConditionalAction
from . import *

conditional_actions = []


def open_bag_condition() -> bool:
    time.sleep(1)
    return not info.bagIsOpen


def open_bag_action() -> bool:
    return echo_bag_lock_open_bag_action()


open_bag = ConditionalAction(
    name="打开背包声骸",
    condition=open_bag_condition,
    action=open_bag_action,
)
conditional_actions.append(open_bag)




