# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: dreamless.py
@time: 2024/6/5 上午10:23
@author SuperLazyDog
"""
# 无妄者脚本
from . import *

pages = []


# 进入
def enter_action(positions: dict[str, Position]) -> bool:
    """
    进入
    :param positions: 位置信息
    :return:
    """
    interactive()
    info.inDreamless = True
    return True


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
    result = wait_text("推荐等级40")
    if not result:
        control.esc()
        return False
    for i in range(3):
        click_position(result.position)
        time.sleep(1)
    result = find_text("单人挑战")
    if not result:
        control.esc()
        return False
    click_position(result.position)
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


# 离开
def leave_action(positions: dict[str, Position]) -> bool:
    """
    离开
    :param positions: 位置信息
    :return:
    """
    if find_text("领取"):
        for i in range(10):
            forward()
    for i in range(3):
        interactive()
        time.sleep(1)
    control.esc()
    time.sleep(1)
    return True


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
    control.click(1250 * width_ratio, 650 * height_ratio)
    time.sleep(3)
    wait_home()
    logger("无妄者副本结束")
    info.inDreamless = False
    info.status = Status.idle
    info.resetTime()
    return True


confirm_leave_page = Page(
    name="确认离开",
    targetTexts=[
        TextMatch(
            name="确认离开",
            text="确认离开",
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
