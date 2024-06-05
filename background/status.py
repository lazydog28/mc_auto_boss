# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: status.py
@time: 2024/6/5 上午9:41
@author SuperLazyDog
"""
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


class Status(Enum):
    idle = "空闲"
    fight = "战斗"


class StatusInfo(BaseModel):
    roleIndex: int = Field(0, title="角色索引")
    bossIndex: int = Field(0, title="boss索引")
    status: Status = Field(Status.idle, title="状态")
    fightTime: datetime = Field(datetime.now(), title="战斗开始时间")
    lastFightTime: datetime = Field(datetime.now(), title="最近检测到战斗时间")
    idleTime: datetime = Field(datetime.now(), title="空闲时间")
    startTime: datetime = Field(datetime.now(), title="开始时间")
    lastSelectRoleTime: datetime = Field(datetime.now(), title="最近选择角色时间")
    currentPageName: str = Field("", title="当前页面名称")


info = StatusInfo()

lastMsg = ""


def logger(msg: str):
    global lastMsg
    content = (
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
        f"当前角色状态：{info.status} "
        f"{msg}"
    )
    start = "\n" if lastMsg != msg else "\r"
    content = start + content
    print(content, end="")
    lastMsg = msg
