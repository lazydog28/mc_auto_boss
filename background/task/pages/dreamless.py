# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: dreamless.py
@time: 2024/6/5 上午10:23
@author SuperLazyDog
"""
# 周本BOSS脚本

import time
from . import *
from datetime import timedelta
from status import Status, info
from schema import ConditionalAction

pages = []


# 进入
def enter_action(positions: dict[str, Position]) -> bool:
    """
    进入
    :param positions: 位置信息
    :return:
    """
    if info.bossTrueName == "无妄者":
        interactive()
        info.inDreamless = True
        info.lastBossName = "无妄者"
        info.inDungeon = True
        return True
    if info.bossTrueName == "角":
        interactive()
        info.inJue = True
        info.lastBossName = "角"
        info.inDungeon = True
        return True


def add_enter_page():
    enter_page = Page(
        name="进入",
        targetTexts=[
            TextMatch(
                name="进入",
                text="进入",
            ),
        ],
        excludeTexts=[
            TextMatch(
                name="确认",
                text="确认",
            ),
        ],
        action=enter_action,
    )
    pages.append(enter_page)


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
    elif config.DungeonWeeklyBossLevel is None or config.DungeonWeeklyBossLevel < 40 or config.DungeonWeeklyBossLevel % 10 != 0:
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
    for i in range(4):
        click_position(result.position)
        time.sleep(0.2)
    result = find_text("单人挑战")
    if not result:
        control.esc()
        return False
    logger(f"最低推荐等级为{dungeon_weekly_boss_level}级")
    time.sleep(0.2)
    click_position(result.position)
    info.waitBoss = True
    info.lastFightTime = datetime.now()
    time.sleep(0.5)


def add_recommended_level_page():
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
    for _ in range(3):
        click_position(position)
        time.sleep(0.2)
    info.lastFightTime = datetime.now()
    time.sleep(1)
    check_loading()
    return True


def add_start_challenge_page():
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


# 离开
def leave_action(positions: dict[str, Position]) -> bool:
    """
    离开
    :param positions: 位置信息
    :return:
    """
    # if info.needAbsorption and config.SearchDreamlessEchoes:
    # absorption_action()
    #    add_judgment_absorption_condition_action()
    # else:
    #     absorption_and_receive_rewards({})
    if (not ((datetime.now() - info.lastFightTime).seconds < config.MaxIdleTime)
            or not info.needAbsorption
            or not config.SearchDreamlessEchoes):
        control.esc()
        time.sleep(1)
        return True


def add_leave_page():
    leave_page = Page(
        name="离开",
        targetTexts=[
            TextMatch(
                name="离开",
                text="离开",
            ),
        ],
        excludeTexts=[
            TextMatch(
                name="确认",
                text="确认",
            ),
        ],
        action=leave_action,
    )

    pages.append(leave_page)


# 确认离开
def confirm_leave_action(positions: dict[str, Position]) -> bool:
    """
    确认离开
    :param positions: 位置信息
    :return:
    """
    click_position(positions["确认"])
    info.echoSearchEndTime = datetime.now()
    time.sleep(0.5)
    i = 0
    while not check_loading(leave_dungeon=True):
        i += 1
        if find_text("确认"):
            click_position(positions["确认"])
            time.sleep(0.5)
        elif i >= 3:
            logger("超过循环次数，无法确认是否成功离开副本")
            break
        else:
            control.esc()
            time.sleep(1)
    while check_in_animation() != "is available":
        control.esc()
        time.sleep(1)
    # wait_home()
    logger(f"{info.bossTrueName}副本结束")
    time.sleep(0.5)
    info.inJue = False
    info.inDreamless = False
    info.inDungeon = False
    info.needAbsorption = False
    info.status = Status.idle
    now = datetime.now()
    info.lastFightTime = now + timedelta(seconds=config.MaxFightTime / 2)
    return True


def add_confirm_leave_page():
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


def add_crystal_wave_page():
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


if info.status != Status.fight:  # 非战斗状态判断全部页面
    add_enter_page()  # 进入和确认
    add_recommended_level_page()  # 推荐等级
    add_start_challenge_page()  # 开启挑战
    add_leave_page()  # 离开和确认
    add_confirm_leave_page()  # 确认离开
    add_crystal_wave_page()  # 结晶波片不足
else:  # 战斗状态只添加部分战斗相关页面 以提高战斗代码执行效率
    add_confirm_leave_page()  # 确认离开
    add_crystal_wave_page()  # 结晶波片不足
