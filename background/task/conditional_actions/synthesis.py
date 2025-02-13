# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: synthesis.py
@time: 2024/6/5 下午1:46
@author wakening
"""
import sys

from schema import ConditionalAction
from . import *

conditional_actions = []


def open_data_merge_condition() -> bool:
    return info.needOpenDataMerge and not info.dataMergeFinish


def open_data_merge_action() -> bool:
    control.activate()
    time.sleep(0.2)
    control.esc()
    time.sleep(2)
    return True


open_data_merge = ConditionalAction(
    name="前往数据融合",
    condition=open_data_merge_condition,
    action=open_data_merge_action,
)
conditional_actions.append(open_data_merge)


def go_back_home_page_condition() -> bool:
    return info.dataMergeFinish


def go_back_home_page_action() -> bool:
    if find_text(["数据坞信息", "数据融合"]):
        control.esc()
        time.sleep(2)
    if find_text("终端"):
        control.esc()
        time.sleep(2)
        if not find_text("终端"):
            logger("已返回大世界")
            sys.exit(0)
    return True


go_back_home_page = ConditionalAction(
    name="离开数据融合",
    condition=go_back_home_page_condition,
    action=go_back_home_page_action,
)
conditional_actions.append(go_back_home_page)



