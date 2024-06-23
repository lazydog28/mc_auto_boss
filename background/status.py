# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: status.py
@time: 2024/6/5 上午9:41
@author SuperLazyDog
"""
from enum import Enum
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from config import config
from colorama import init, Fore, Style


class Status(Enum):
    idle = "空闲"
    fight = "战斗"


class StatusInfo(BaseModel):
    roleIndex: int = Field(0, title="角色索引")
    bossIndex: int = Field(0, title="boss索引")
    status: Status = Field(Status.idle, title="状态")
    fightTime: datetime = Field(datetime.now(), title="战斗开始时间")
    fightCount: int = Field(0, title="战斗次数")
    absorptionCount: int = Field(0, title="吸收次数")
    absorptionSuccess: bool = Field(False, title="吸收成功")
    needAbsorption: bool = Field(False, title="需要吸收")
    lastFightTime: datetime = Field(
        datetime.now() + timedelta(seconds=config.MaxIdleTime / 2),
        title="最近检测到战斗时间",
    )
    idleTime: datetime = Field(datetime.now(), title="空闲时间")
    startTime: datetime = Field(datetime.now(), title="开始时间")
    lastSelectRoleTime: datetime = Field(datetime.now(), title="最近选择角色时间")
    currentPageName: str = Field("", title="当前页面名称")
    inDreamless: bool = Field(False, title="是否在无妄者副本内")
    lastBossName: str = Field("", title="最近BOSS名称")
    healCount: int = Field(0, title="治疗次数")
    needHeal: bool = Field(False, title="需要治疗")
    checkHeal: bool = Field(True, title="检查角色存活情况")
    waitBoss: bool = Field(True, title="检查角色存活情况")
    echoNumber: int = Field(0, title="当前进行的锁定声骸个数")
    echoIsLockQuantity: int = Field(0, title="检测到连续锁定的声骸数量")
    DungeonWeeklyBossLevel: int = Field(0, title="储存自动判断出的最低可获奖励副本BOSS的等级")

    def resetTime(self):
        self.fightTime = datetime.now()
        self.idleTime = datetime.now()
        self.lastFightTime = datetime.now()


info = StatusInfo()

lastMsg = ""


def logger(msg: str, level: str = "INFO", display: bool = True):
    global lastMsg
    content = (
        f"【{level}】 "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
        f"战斗次数：{info.fightCount} "
        f"吸收次数：{info.absorptionCount} "
    )
    if config.CharacterHeal:
        content += f"治疗次数：{info.healCount} "
    content += f"{msg}"

    start = "\n" if lastMsg != msg else "\r"
    content = start + content

    # 设置日志级别颜色
    if level == "INFO":
        color = Fore.WHITE
    elif level == "WARN":
        color = Fore.YELLOW
    elif level == "ERROR":
        color = Fore.RED
    elif level == "DEBUG":
        color = Fore.GREEN
    else:
        color = Fore.WHITE
    colored_content = color + content

    if display:
        print(colored_content, end="")
        lastMsg = msg

    with open(config.log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write(content)
