# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: general.py
@time: 2024/6/5 上午9:34
@author SuperLazyDog
"""
from . import *

pages = []


# 吸收声骸
def absorption_action(positions: dict[str, Position]) -> bool:
    """
    吸收声骸
    :param positions: 位置信息
    :return:
    """
    time.sleep(2)
    if not find_text("吸收"):
        return False
    info.absorptionCount += 1
    interactive()
    time.sleep(2)
    info.needAbsorption = False
    return True


absorption_page = Page(
    name="吸收",
    targetTexts=[
        TextMatch(
            name="吸收",
            text="吸收",
        ),
    ],
    excludeTexts=[
        TextMatch(
            name="领取奖励",
            text="领取奖励",
        ),
    ],
    action=absorption_action,
)

pages.append(absorption_page)


# 选择复苏物品
def select_recovery_items(positions: dict[str, Position]) -> bool:
    """
    取消选择复苏物品
    :param positions:
    :return:
    """
    info.needHeal = True
    logger("队伍中有角色需要复苏")
    control.esc()
    return True


select_recovery_items_page = Page(
    name="选择复苏物品",
    targetTexts=[
        TextMatch(
            name="选择复苏物品",
            text="选择复苏物品",
        ),
    ],
    action=select_recovery_items,
)
pages.append(select_recovery_items_page)


# 退出副本
def exit_instance(positions: dict[str, Position]) -> bool:
    """
    退出副本
    :param positions:
    :return:
    """
    position = positions.get("退出副本", None)
    if position is None:
        return False
    click_position(position)
    return True


exit_instance_page = Page(
    name="退出副本",
    targetTexts=[
        TextMatch(
            name="退出副本",
            text="退出副本",
        ),
    ],
    action=exit_instance,
)

pages.append(exit_instance_page)


# 终端
def terminal_action(positions: dict[str, Position]) -> bool:
    """
    终端
    :param positions: 位置信息
    :return:
    """
    control.esc()
    time.sleep(2)
    return True


terminal_page = Page(
    name="终端",
    targetTexts=[
        TextMatch(
            name="终端",
            text="终端",
        ),
    ],
    action=terminal_action,
)

pages.append(terminal_page)


# 击败 战斗状态
def fight_action(positions: dict[str, Position]) -> bool:
    """
    击败 战斗状态
    :param positions: 位置信息
    :return:
    """
    if info.status != Status.fight:
        if info.inDreamless and config.DreamlessWaitTime > 0:
            logger(f"无妄者副本战斗延迟{config.DreamlessWaitTime}")
            time.sleep(config.DreamlessWaitTime)
        info.fightCount += 1
        info.needAbsorption = True
        info.fightTime = datetime.now()
    release_skills()
    info.status = Status.fight
    info.lastFightTime = datetime.now()
    return True


fight_page = Page(
    name="战斗画面",
    targetTexts=[
        TextMatch(
            name="击败",
            text="击败",
        ),
    ],
    action=fight_action,
)

pages.append(fight_page)


# 点击领取今日月卡奖励
def click_receive_monthly_card_rewards(positions: dict[str, Position]) -> bool:
    """
    点击领取今日月卡奖励
    :param positions: 位置信息
    :return:
    """
    position = positions.get("月卡奖励", None)
    if position is None:
        return False
    click_position(position)
    control.click(960 * width_ratio, 540 * height_ratio)
    return True


receive_monthly_card_rewards_page = Page(
    name="月卡奖励",
    targetTexts=[
        TextMatch(
            name="月卡奖励",
            text="月卡奖励",
        ),
    ],
    action=click_receive_monthly_card_rewards,
)

pages.append(receive_monthly_card_rewards_page)


# 补充结晶波片
def supplement_crystal_wave(positions: dict[str, Position]) -> bool:
    """
    补充结晶波片
    :param positions: 位置信息
    :return:
    """
    control.esc()  # 退出
    time.sleep(2)
    return True


supplement_crystal_wave_page = Page(
    name="补充结晶波片",
    targetTexts=[
        TextMatch(
            name="补充结晶波片",
            text="补充结晶波片",
        ),
    ],
    action=supplement_crystal_wave,
)
pages.append(supplement_crystal_wave_page)


# 领取奖励
def receive_rewards(positions: dict[str, Position]) -> bool:
    """
    领取奖励
    :param positions: 位置信息
    :return:
    """
    control.esc()  # 退出
    time.sleep(2)
    return True


receive_rewards_page = Page(
    name="领取奖励",
    targetTexts=[
        TextMatch(
            name="领取奖励",
            text="领取奖励",
        ),
        TextMatch(
            name="确认",
            text="确认",
        ),
    ],
    action=receive_rewards,
)
pages.append(receive_rewards_page)

absorption_and_receive_rewards_page = Page(
    name="吸收和领取奖励重合",
    targetTexts=[
        TextMatch(
            name="领取奖励",
            text="领取奖励",
        ),
        TextMatch(
            name="吸收",
            text="吸收",
        ),
    ],
    action=absorption_and_receive_rewards,
)


def blank_area(positions: dict[str, Position]) -> bool:
    """
    空白区域
    :param positions: 位置信息
    :return:
    """
    control.activate()
    control.click(480 * width_ratio, 540 * height_ratio)
    time.sleep(1)
    control.esc()  # 退出
    time.sleep(1)
    return True


blank_area_page = Page(
    name="空白区域",
    targetTexts=[
        TextMatch(
            name="空白区域",
            text="空白区域",
        ),
    ],
    action=blank_area,
)

pages.append(blank_area_page)


# 定义一个名为login_action的函数，接收一个名为positions的字典参数，返回布尔值
def login_action(positions: dict[str, Position]) -> bool:
    try:
        # 调用find_text函数，传入字符串"点击"，将返回值赋给result变量
        result = find_text("点击")
        # 循环3次点击文字
        for i in range(3):
            # 调用click_position函数，传入result.position作为参数
            click_position(result.position)
            # 暂停0.4秒
            time.sleep(0.4)
    # 如果在try语句块中发生异常，执行except语句块中的代码
    except Exception as e:
        # 打印异常信息
        print(f"发生异常： {e}")
        # 继续点击文字"点击连接"
        result = find_text("点击")
        # 循环3次点击文字
        for i in range(3):
            # 调用click_position函数，传入result.position作为参数
            click_position(result.position)
            # 暂停0.4秒
            time.sleep(0.4)
        # 返回False
        return False
    # 如果没有发生异常，返回True
    return True

# 创建一个名为login_page的Page对象
login_page = Page(
    name="点击连接",
    targetTexts=[
        TextMatch(
            name="点击连接",
            text="点击连接",
        ),
    ],  
    action=login_action,
)
# 将login_page对象添加到pages列表中
pages.append(login_page)

