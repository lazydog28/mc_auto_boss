# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: dreamless.py
@time: 2024/6/5 上午10:23
@author SuperLazyDog
"""
import time

# 无妄者脚本
from . import *
from datetime import timedelta

# 防止卡加载
from config import config

pages = []


# 进入
def enter_action_dreamless(positions: dict[str, Position]) -> bool:
    """
    进入
    :param positions: 位置信息
    :return:
    """
    interactive()
    info.inDreamless = True
    info.lastBossName = "无妄者"
    return True


enter_page_dreamless = Page(
    name="无冠者之像·心脏",
    targetTexts=[
        TextMatch(
            name="无冠者之像",
            text="无冠者之像",
        ),
        TextMatch(
            name="进入|离开",
            # 进入是在外面F进入副本页面；
            # 离开是在无妄者副本内战斗结束时，用于游戏闪退重启后直接在副本内触发切换模型
            text=template(r"(进入|离开)"),
        ),
    ],
    excludeTexts=[
        TextMatch(
            name="确认",
            text="确认",
        ),
        TextMatch(
            name="快速旅行",
            text="快速旅行",
        ),
        TextMatch(
            name="领取奖励",
            text="领取奖励",
        ),
    ],
    action=enter_action_dreamless,
)

pages.append(enter_page_dreamless)


# 进入
def enter_action_jue(positions: dict[str, Position]) -> bool:
    """
    进入
    :param positions: 位置信息
    :return:
    """
    interactive()
    info.inJue = True
    info.lastBossName = "角"
    return True


enter_page_jue = Page(
    name="时序之寰",
    targetTexts=[
        TextMatch(
            name="时序之寰",
            text="进入时序之",
        ),
    ],
    excludeTexts=[
        TextMatch(
            name="确认",
            text="确认",
        ),
    ],
    action=enter_action_jue,
)

pages.append(enter_page_jue)


def enter_action_hecate(positions: dict[str, Position]) -> bool:
    """
    进入
    :param positions: 位置信息
    :return:
    """
    interactive()
    info.inHecate = True
    info.lastBossName = "赫卡忒"
    return True


enter_page_hecate = Page(
    name="声之领域",
    targetTexts=[
        TextMatch(
            name="声之领域",
            text="进入声之领域",
        ),
    ],
    excludeTexts=[
        TextMatch(
            name="确认",
            text="确认",
        ),
    ],
    action=enter_action_hecate,
)

pages.append(enter_page_hecate)


# 推荐等级
def recommended_level_action(positions: dict[str, Position]) -> bool:
    """
    推荐等级
    :param positions: 位置信息
    :return:
    """
    interactive()
    if info.DungeonWeeklyBossLevel != 0:
        dungeon_weekly_boss_level = info.DungeonWeeklyBossLevel  # 如果已有自动搜索结果，那么直接使用自动搜索的结果值
    elif (
        config.DungeonWeeklyBossLevel is None
        or config.DungeonWeeklyBossLevel < 40
        or config.DungeonWeeklyBossLevel % 10 != 0):
        dungeon_weekly_boss_level = 40  # 如果没有自动搜索的结果，且没有Config值或为值异常，则从40开始判断
    else:
        dungeon_weekly_boss_level = config.DungeonWeeklyBossLevel  # 如果没有自动搜索的结果，但有Config值且不为默认值，则使用Config值
    result = wait_text("推荐等级" + str(dungeon_weekly_boss_level))
    if not result:
        for i in range(1, 5):
            control.esc()
            result = wait_text("推荐等级" + str(dungeon_weekly_boss_level + (10 * i)))
            if result:
                info.DungeonWeeklyBossLevel = dungeon_weekly_boss_level + (10 * i)
                break
    if not result:
        control.esc()
        return False
    for i in range(2):
        click_position(result.position)
        time.sleep(0.5)
    result = find_text("单人挑战")
    if not result:
        control.esc()
        return False
    logger(f"最低推荐等级为{dungeon_weekly_boss_level}级")
    click_position(result.position)
    info.waitBoss = True
    info.lastFightTime = datetime.now()
    time.sleep(1)


recommended_level_page = Page(
    name="推荐等级",
    targetTexts=[
        TextMatch(
            name="推荐等级",
            text="推荐等级",
        ),
    ],
    action=recommended_level_action,
)

pages.append(recommended_level_page)


# 开启挑战
def start_challenge_action(positions: dict[str, Position]) -> bool:
    """
    开启挑战
    :param positions: 位置信息
    :return:
    """
    position = positions["开启挑战"]
    click_position(position)
    time.sleep(0.5)
    info.lastFightTime = datetime.now()
    return True


start_challenge_page = Page(
    name="开启挑战",
    targetTexts=[
        TextMatch(
            name="开启挑战",
            text="开启挑战",
        ),
    ],
    action=start_challenge_action,
)
pages.append(start_challenge_page)


# 确认离开
def confirm_leave_action(positions: dict[str, Position]) -> bool:
    """
    确认离开
    :param positions: 位置信息
    :return:
    """
    control.activate()
    time.sleep(0.2)
    if need_retry() and not info.needHeal:
        click_position(positions["重新挑战"])
        logger(f"重新挑战{info.lastBossName}副本")
        if not info.lastBossName:
            info.lastBossName = config.TargetBoss[0]
            model_boss_yolo(info.lastBossName)
        time.sleep(4)
        if info.lastBossName == "角":
            info.inJue = True
        elif info.lastBossName == "无妄者":
            info.inDreamless = True
        elif info.lastBossName == "赫卡忒":
            info.inHecate = True
        info.status = Status.idle
        now = datetime.now()
        info.lastFightTime = now
        info.fightTime = now
        info.waitBoss = True
    else:
        pos = positions.get("确认", positions.get("退出副本"))
        click_position(pos)
        time.sleep(3)
        wait_home()
        logger(f"{info.lastBossName}副本结束")
        time.sleep(2)
        if info.lastBossName == "角":
            info.inJue = False
        elif info.lastBossName == "无妄者":
            info.inDreamless = False
        elif info.lastBossName == "赫卡忒":
            info.inHecate = False
        info.status = Status.idle
        now = datetime.now()
        info.lastFightTime = now + timedelta(seconds=config.MaxFightTime / 2)
    info.isCheckedHeal = False
    return True


confirm_leave_page = Page(
    name="确认离开",
    targetTexts=[
        TextMatch(
            name="确认离开",
            text="确认离开",
        ),
        TextMatch(
            name="确认",
            text=template("^确认$"),
        ),
        TextMatch(
            name="重新挑战",
            text=template("^重新挑战$"),
        ),
    ],
    action=confirm_leave_action,
)

pages.append(confirm_leave_page)


# 结晶波片不足
def crystal_wave_action(positions: dict[str, Position]) -> bool:
    """
    结晶波片不足
    :param positions: 位置信息
    :return:
    """
    position = positions["确认"]
    click_position(position)
    time.sleep(2)
    return True


crystal_wave_page = Page(
    name="结晶波片不足",
    targetTexts=[
        TextMatch(
            name="结晶波片不足",
            text="结晶波片不足",
        ),
        TextMatch(
            name="确认",
            text=template("^确认$"),
        ),
    ],
    action=crystal_wave_action,
)

pages.append(crystal_wave_page)
