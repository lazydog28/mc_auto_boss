# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: general.py
@time: 2024/6/5 上午9:34
@author SuperLazyDog
"""

from schema import Position, ImgPosition, OcrResult, TextMatch, ImageMatch, Page
from control import control
from re import Pattern, template
from status import info, Status, logger
from datetime import datetime, timedelta
from utils import *
import hwnd_util
import time


pages = []


# 游戏更新完成后，通过点击退出按钮来重新启动游戏。
def update_game_exit(positions: dict[str, Position]) -> bool:
    """
    更新完成，请重新启动游戏。
    :param positions: 位置信息
    :return:
    """
    position = positions["退出"]
    click_position(position)
    time.sleep(2)
    return True


def add_update_game_exit_page():
    update_game_exit_page = Page(
        name="更新完成，请重新启动游戏。",
        targetTexts=[
            TextMatch(
                name="更新完成，请重新启动游戏。",
                text="更新完成，请重新启动游戏。",
            ),
            TextMatch(
                name="退出",
                text=template("^退出$"),
            ),
        ],
        action=update_game_exit,
    )
    pages.append(update_game_exit_page)


# 吸收声骸
def absorption_action(positions: dict[str, Position]) -> bool:
    """
    吸收声骸
    :param positions: 位置信息
    :return:
    """
    for i in range(5):
        time.sleep(0.4)
        if not find_text("吸收"):
            return False
        else:
            for _ in range(5):
                control.tap("w")
                interactive()
                time.sleep(0.1)
            if info.absorptionCount == info.lastAbsorptionCount:
                info.absorptionCount += 1
            if info.echoSearchTimesCount == 0:
                info.echoSearchStartTime = datetime.now()
            info.needAbsorption = False
            info.lastFightTime = info.lastFightTime - timedelta(seconds=(config.MaxIdleTime + 5))  # 吸收完成后立即结束等待
            break
    if not info.needAbsorption:
        return True
    else:
        return False


def add_absorption_page():
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
    info.characterHealthyIndex[info.roleIndex] = False
    logger(f"{info.roleIndex}号角色需要治疗")
    control.esc()
    return True

def add_select_recovery_items_page():
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

def add_exit_instance_page():
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

def add_terminal_page():
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
        # if info.inDreamless and config.DreamlessWaitTime > 0:
        #    logger(f"无妄者副本战斗延迟{config.DreamlessWaitTime}")
        #    time.sleep(config.DreamlessWaitTime)
        # 转自BOSS延迟统一调用
        info.fightCount += 1
        info.needAbsorption = True
        info.fightTime = datetime.now()
        info.searchTimes = 0
    info.status = Status.fight
    release_skills()
    info.lastFightTime = datetime.now()
    return True


def add_fight_page():
    fight_page = Page(
        name="战斗画面",
        targetTexts=[
            TextMatch(
                name="战斗",
                text=template(r"(击败|对战)"),  # 使用正则表达式匹配 支持击败和对战
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
    while check_in_animation() != "is available":
        control.click(600 * width_ratio, 600 * height_ratio)
        time.sleep(0.5)
    return True


def add_receive_monthly_card_rewards_page():
    receive_monthly_card_rewards_page = Page(
        name="月卡奖励",
        targetTexts=[
            TextMatch(
                name="月卡奖励",
                text="今日月相",
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


def add_supplement_crystal_wave_page():
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
    time.sleep(1)
    control.esc()
    return True


def add_receive_rewards_page():
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


# 吸收和领取奖励重合
def add_absorption_and_receive_rewards_page():
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


def add_blank_area_page():
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
def link_action(positions: dict[str, Position]) -> bool:
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
        check_game_restarting(del_file=True)
        return False
    # 如果没有发生异常，返回True
    check_game_restarting(del_file=True)
    return True


def add_link_page():
    # 创建一个名为login_page的Page对象
    login_page = Page(
        name="点击连接",
        targetTexts=[
            TextMatch(
                name="点击连接",
                text="点击连接",
            ),
        ],
        action=link_action,
    )
    # 将login_page对象添加到pages列表中
    pages.append(login_page)


def confirm_page_action(positions: dict[str, Position]) -> bool:
    """
    更新完成，请重新启动游戏。
    :param positions: 位置信息
    :return:
    """
    position = positions["确认"]
    click_position(position)
    time.sleep(2)
    return True


def add_disconnected_page():
    disconnected_page = Page(
        name="连接已断开",
        targetTexts=[
            TextMatch(
                name="连接已断开",
                text="连接已断开",
            ),
            TextMatch(
                name="登录超时，请重新尝试。",
                text="登录超时",
            ),
            TextMatch(
                name="确认",
                text=template("^确认$"),
            ),
        ],
        action=confirm_page_action,
    )
    pages.append(disconnected_page)


def add_network_timeout_page():
    network_timeout_page = Page(
        name="系统提示",
        targetTexts=[
            TextMatch(
                name="系统提示",
                text="系统提示",
            ),
            TextMatch(
                name="网络请求超时，无法连接服务器，请稍后再尝试。",
                text="网络请求超时",
            ),
            TextMatch(
                name="确认",
                text=template("^确认$"),
            ),
        ],
        action=confirm_page_action,
    )
    pages.append(network_timeout_page)


def account_login_action(positions: dict[str, Position]) -> bool:
    def click_login_page(ck_login_hwnd):
        try:
            ocr_text_result = find_text_in_login_hwnd("^登录$", ck_login_hwnd)
            if ocr_text_result is None:
                return False
            # 文本相对于登录框的位置
            # logger(f"position: {ocr_text_result.position}")
            click_position_in_login_hwnd(ocr_text_result.position, specified_hwnd=ck_login_hwnd)
        except Exception as e:
            pass
        time.sleep(3)
        return True

    # 手机号登录窗口特殊，是遮盖在游戏上方的另一个窗口句柄，费老半天才搞明白 by wakening
    # 调用游戏窗口截图会截取到登录窗口下层的游戏窗口，点击也是点不到上层
    # 先试官服
    login_hwnd_list = hwnd_util.get_login_hwnd_official()
    if login_hwnd_list is not None and len(login_hwnd_list) > 0:
        for login_hwnd in login_hwnd_list:
            if click_login_page(login_hwnd):
                logger("官服点击登录")
                return True

    # 再试b服
    login_hwnd = hwnd_util.get_login_hwnd_bilibili()
    if click_login_page(login_hwnd):
        logger("b服点击登录")
        return True

    # logger("未找到登录页面")
    time.sleep(5)
    return False


# 游戏掉线等原因出现的登录窗口，覆盖在游戏窗口之上，
# 点击登录后才会出现点击连接，以此区分
def add_account_login_page():
    account_login_page = Page(
        name="账户登录",
        targetTexts=[
            TextMatch(
                name="退出",
                text="退出",
            ),
            TextMatch(
                name="登入",
                text="登入",
            ),

        ],
        excludeTexts=[
            TextMatch(
                name="点击连接",
                text="点击连接",
            ),
        ],
        action=account_login_action,
    )
    pages.append(account_login_page)


if info.status != Status.fight:  # 非战斗状态判断全部页面
    add_update_game_exit_page()  # 游戏更新完成
    add_absorption_page()  # 吸收和领取奖励
    add_select_recovery_items_page()  # 选择复苏道具
    add_exit_instance_page()  # 退出副本
    add_terminal_page()  # 终端
    add_fight_page()  # 战斗画面
    add_receive_monthly_card_rewards_page()  # 月卡奖励
    add_supplement_crystal_wave_page()  # 补充结晶碎片
    add_receive_rewards_page()  # 领取奖励和确认
    add_blank_area_page()  # 空白区域
    add_link_page()  # 点击链接
    add_absorption_and_receive_rewards_page()  # 吸收和领取奖励重合
    add_disconnected_page()  # 连接已断开
    add_network_timeout_page()  # 网络请求超时
    add_account_login_page()  # 点击登入
else:  # 战斗状态只添加部分战斗相关页面 以提高战斗代码执行效率
    add_fight_page()  # 战斗画面
    add_select_recovery_items_page()  # 选择复苏道具
    add_receive_monthly_card_rewards_page()  # 月卡奖励
    add_blank_area_page()  # 空白区域
