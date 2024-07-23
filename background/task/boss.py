# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: __init__.py.py
@time: 2024/6/5 下午1:40
@author SuperLazyDog
"""
import importlib
from schema import Task
import status
from status import Status, info
from .pages import general as general_pages
from .pages import boss as boss_pages
from .pages import dreamless as dreamless_pages
from .conditional_actions import boss as conditional_actions_boss


# 重新加载页面和条件操作
def reload_pages_and_conditional_actions():
    # 重新加载页面
    general_pages.pages.clear()
    boss_pages.pages.clear()
    dreamless_pages.pages.clear()
    conditional_actions_boss.conditional_actions.clear()

    importlib.reload(general_pages)
    importlib.reload(boss_pages)
    importlib.reload(dreamless_pages)
    importlib.reload(conditional_actions_boss)

    pages = general_pages.pages + boss_pages.pages + dreamless_pages.pages
    conditional_actions = conditional_actions_boss.conditional_actions
    return pages, conditional_actions
