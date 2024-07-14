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
from read_crashes_data import read_crashes_datas
from typing import Tuple, List


class Status(Enum):
    idle = "空闲"
    fight = "战斗"

# 如果游戏发生了崩溃则会创建文本文件isCrashes.txt，写入布尔值True
# F5重启脚本后，会触发readCrashesDatas函数
# 通过IO读取布尔值判断是否处于崩溃状态
# 如果为True  则读取日志中的崩溃的值作为当前的数据，包含：战斗次数,吸收次数，治疗次数，作为当前日志的记录
# 如果为False 或者该文本文件不存在，则使用默认值0，作为当前的日志记录


battle_count, absorb_count, heal_count = read_crashes_datas()


class StatusInfo(BaseModel):
    
    roleIndex: int = Field(0, title="角色索引")
    lastRoleIndex: int = Field(0, title="最后一次角色索引")
    characterHealthyIndex: List[bool] = Field([True, True, True, True], title="角色存活状态")   # 实质上从[1]到[3]
    bossIndex: int = Field(0, title="boss索引")
    status: Status = Field(Status.idle, title="状态")
    fightTime: datetime = Field(datetime.now(), title="战斗开始时间")
    fightCount: int = Field(battle_count, title="战斗次数")
    absorptionCount: int = Field(absorb_count, title="吸收次数")
    lastAbsorptionCount: int = Field(absorb_count, title="吸收次数")
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
    inJue: bool = Field(False, title="是否在角副本内")
    lastBossName: str = Field("", title="最近BOSS名称")
    bossTrueName: str = Field("", title="当前BOSS正式名称")
    echoSearchModel: str = Field("yolo.onnx", title="寻找声骸的模型")
    healCount: int = Field(heal_count, title="治疗次数")
    needHeal: bool = Field(False, title="需要治疗")
    checkHeal: bool = Field(True, title="检查角色存活情况")
    waitBoss: bool = Field(True, title="等待Boss时间")
    DungeonWeeklyBossLevel: int = Field(0, title="储存自动判断出的最低可获奖励副本BOSS的等级")
    resetRole: bool = Field(False, title="重置选择角色")
    adaptsType: int = Field(None, title="适配类型")
    adaptsResolution: str = Field(None, title="适配分辨率")
    consumablesInfo: List = Field([], title="消耗品信息")
    consumablesEndTime: datetime = Field(datetime.now(), title="消耗品结束时间")
    inGame: bool = Field(False, title="是否在游戏中")
    fightEndTime: datetime = Field(datetime.now(), title="战斗结束时间")
    echoSearchStartTime: datetime = Field(datetime.now(), title="搜索声骸开始时间")
    echoSearchEndTime: datetime = Field(datetime.now(), title="搜索声骸结束时间")
    echoSearchTimesCount: int = Field(0, title="搜索声骸次数")
    # 声骸功能Status
    echoIsLockQuantity: int = Field(0, title="检测到连续锁定的声骸数量")
    echoNumber: int = Field(0, title="当前进行的锁定声骸个数")
    inSpecEchoQuantity: int = Field(0, title="检测到的符合配置的声骸数量")
    synthesisGoldQuantity: int = Field(0, title="合成声骸数量")
    synthesisTimes: int = Field(0, title="声骸合成次数")
    inSpecSynthesisEchoQuantity: int = Field(0, title="合成的符合配置的声骸数量")
    searchStartTime: datetime = Field(datetime.now(), title="搜索声骸开始时间")
    searchTimes: int = Field(0, title="声骸搜索次数")
    fKeyWaitTime: datetime = Field(datetime.now(), title="按F后的等待时间")
    fightEndFlag: bool = Field(False, title="战斗结束标志")
    fightEndFlagCount: int = Field(False, title="用于判断战斗结束标志的计数")
    actionErrorTimes: int = Field(0, title="动作错误次数")
    lastActionErrorTime: datetime = Field(datetime.now(), title="最后一次动作错误时间")
    lastStatus: Status = Field(Status.idle, title="最后状态")

    def resetTime(self):
        self.fightTime = datetime.now()
        self.idleTime = datetime.now()
        self.lastFightTime = datetime.now()


info = StatusInfo()

lastMsg = ""
last_echo_efficiency_print_time = datetime.now()


def logger(msg: str, level: str = "INFO", display: bool = True):
    global lastMsg, last_echo_efficiency_print_time
    if (datetime.now() - last_echo_efficiency_print_time).total_seconds() > 300:  # 5分钟打印一次
        process_time = datetime.now() - info.startTime
        hours, remainder = divmod(process_time.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        formatted_process_time = f'{int(hours):02}小时{int(minutes):02}分钟{int(seconds):02}秒'
        echo_efficiency = round((process_time.total_seconds() / info.absorptionCount if info.absorptionCount > 0 else 0), 0)
    else:
        echo_efficiency = None
        formatted_process_time = None
    content = (
        f"【{level}】 "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
        f"战斗次数：{info.fightCount} "
        f"吸收次数：{info.absorptionCount} "
    )
    if config.CharacterHeal:
        content += f"治疗次数：{info.healCount} "
        if info.fightCount > 0:
            content += f"吸收率：{round((info.absorptionCount / info.fightCount) * 100, 2)}% "
    content += f"{msg}"
    if formatted_process_time and echo_efficiency:
        content += f"\n【{level}】 已运行时间：{formatted_process_time}，声骸获取效率：{echo_efficiency} 秒/个，"
        last_echo_efficiency_print_time = datetime.now()

    if formatted_process_time and echo_efficiency:
        start = "\n"
    else:
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
    elif level == "IMPORTANT":
        color = Fore.YELLOW
    else:
        color = Fore.WHITE
    colored_content = color + content

    if display:
        print(colored_content, end="")
        lastMsg = msg

    with open(config.LogFilePath, 'a', encoding='utf-8') as log_file:
        log_file.write(content)
