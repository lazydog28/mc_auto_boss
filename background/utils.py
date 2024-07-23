# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: operation.py
@time: 2024/5/26 下午9:17
@author SuperLazyDog
"""
import re
import time
import win32gui
import win32ui
import win32process
import os
import win32con
import numpy as np
import itertools
import psutil
import yaml
import importlib
import yolo
from PIL import Image, ImageGrab
from ctypes import windll
from typing import List, Tuple, Union
from constant import root_path, hwnd, real_w, real_h, width_ratio, height_ratio, scale_factor
from ocr import ocr
from schema import match_template, OcrResult
from control import control
from config import config
from status import info, logger
from schema import Position
from datetime import datetime, timedelta
from yolo import search_echoes
from database_echo import echo
from database_consumables import consumables


def interactive():
    control.tap("f")


def click_position(position: Position):
    """
    点击位置
    :param position: 需要点击的位置
    """
    # 分析position的中点
    x = (position.x1 + position.x2) // 2
    y = (position.y1 + position.y2) // 2
    # control.click(x, y)
    random_click(x, y, ratio=False)  # 找图所得坐标不需要缩放！


# 实验性:连招从行读取修改为逐一按键读取，以避免打完BOSS后继续释放技能的问题
current_tactic_index = 0
current_tactic_step = 0
tactic_ult_flag = False
last_tactic_index = 0
this_character_element = "未知"
this_character_element_color = (0, 0, 0)
concerto_energy_flag = False


def select_role(reset_role: bool = False):
    global current_tactic_index, current_tactic_step, last_tactic_index, tactic_ult_flag, this_character_element, \
        this_character_element_color, concerto_energy_flag
    if reset_role:
        info.roleIndex = 1
        current_tactic_index = 0
        current_tactic_step = 0
        last_tactic_index = 0
        tactic_ult_flag = False
        concerto_energy_flag = False
        info.resetRole = False
    if last_tactic_index != current_tactic_index:
        info.roleIndex += 1
        last_tactic_index = current_tactic_index
        if info.roleIndex > 3:
            info.roleIndex = 1
        while not info.characterHealthyIndex[info.roleIndex]:
            logger(f"{info.roleIndex}号角色已阵亡，跳过", "DEBUG")
            info.needHeal = True
            info.roleIndex += 1
            if info.roleIndex > 3:
                info.roleIndex = 1
    if info.roleIndex != info.lastRoleIndex:
        for _ in range(20):
            img = screenshot()
            if check_in_animation(img) != "is animation":
                if this_character_element != "未知":
                    last_character_concerto_energy = check_character_concerto_energy(
                        element_color=this_character_element_color, threshold=0.8)
                    if last_character_concerto_energy == "100%":
                        logger(
                            f"当前退场角色协奏条为:{last_character_concerto_energy}，切换下一角色时将释放自身延奏退场技和下一角色变奏入场技",
                            "DEBUG")
                        concerto_energy_flag = True
                    else:
                        logger(f"当前退场角色协奏条为:{last_character_concerto_energy}", "DEBUG")
                        concerto_energy_flag = False
                control.tap(str(info.roleIndex))
                img = screenshot()
                if check_character_change(img):
                    this_character_element, this_character_element_color = check_character_element(img)
                    logger(f"切换到{info.roleIndex}号角色成功，当前角色属性为:{this_character_element}")
                    current_tactic_step = 0
                    info.lastRoleIndex = info.roleIndex
                    break
                else:
                    time.sleep(0.2)
                    logger(f"切换角色失败，等待0.2秒后重试")


def release_skills():
    global current_tactic_index, current_tactic_step, last_tactic_index, tactic_ult_flag, this_character_element, \
        this_character_element_color, concerto_energy_flag
    if datetime.now() - info.fightTime > timedelta(seconds=300):
        if info.inJue or info.inDreamless:
            logger("战斗超时(5分钟)，退出副本")
            control.esc()
            time.sleep(1)
            return
        else:
            logger("战斗超时(5分钟)，传送回神像")
            info.needHeal = True
            control.activate()
            time.sleep(0.5)
            control.tap(win32con.VK_F2)
            transfer_to_heal()
            return
    if info.waitBoss:
        check_boss(info.lastBossName, True)
    select_role(info.resetRole)
    control.mouse_middle()
    if len(config.FightTactics) < info.roleIndex:
        config.FightTactics.append("e,q,r,a(2)")
    # 获取当前连招
    # 大招释放后的连招(如有配置，无配置则采用常时连招)
    if tactic_ult_flag:
        if current_tactic_step == 0:
            logger("使用大招后连招", "DEBUG")
        tactics = config.FightTacticsUlt[info.roleIndex - 1].split(",")
    # 变奏入场连招(如有配置，无配置则采用常时连招)
    elif concerto_energy_flag:
        if current_tactic_step == 0:
            logger("角色变奏入场，等待变奏技能释放", "DEBUG")
            time.sleep(0.6)
            logger("使用变奏连招", "DEBUG")
        tactics = config.FightTacticsConcerto[info.roleIndex - 1].split(",")
    # 常时连招
    else:
        if current_tactic_step == 0:
            logger("使用通常连招", "DEBUG")
        tactics = config.FightTactics[info.roleIndex - 1].split(",")
    if len(tactics) < 2 or tactics[0] == "e" or tactics is None:
        if current_tactic_step == 0:
            logger("没有查找到连招配置，使用通常连招", "DEBUG")
        tactics = config.FightTactics[info.roleIndex - 1].split(",")
    tactics = split_tactics(tactics)
    # logger(f"当前执行第：{current_tactic_step}/{len(tactics)}个技能", "DEBUG")
    if current_tactic_step >= len(tactics):
        current_tactic_step = 0
        last_tactic_index = current_tactic_index
        current_tactic_index += 1
        if tactic_ult_flag:
            tactic_ult_flag = False
            logger("大招后连段结束", "DEBUG")
        if current_tactic_index >= len(config.FightTactics):
            current_tactic_index = 0

    # logger(f"current_tactic_step/len(tactics) = {current_tactic_step}/{len(tactics)}", "DEBUG")
    # logger(f"当前执行技能列表 {tactics}", "DEBUG")
    # logger(f"当前执行技能 {tactics[current_tactic_step]}", "DEBUG")

    # 执行当前连招中的一个操作（,分割）
    if current_tactic_step < len(tactics):
        tactic = tactics[current_tactic_step]
        try:
            wait_time = float(tactic)  # 如果是数字，等待时间
            time.sleep(wait_time)
        except ValueError:
            time.sleep(np.random.uniform(0, 0.02))  # 随机等待
            if len(tactic) == 1:  # 如果只有一个字符，且为普通攻击，进行连续0.3s的点击
                if tactic == "a":
                    continuous_tap_time = 0.3
                    tap_start_time = time.time()
                    while time.time() - tap_start_time < continuous_tap_time:
                        control.fight_click()
                elif tactic == "s":
                    control.fight_space()
                elif tactic == "r":  # 大招时判断是否释放
                    control.fight_tap(tactic)
                    time.sleep(0.5)
                    if config.WaitUltAnimation:  # 等待大招时间
                        if check_ult():
                            tactic_ult_flag = True
                            current_tactic_step = 0
                            return
                else:
                    control.fight_tap(tactic)
            elif len(tactic) >= 2 and tactic[1] == "~":  # 如果没有指定时间，默认0.5秒
                click_time = 0.5 if len(tactic) == 2 else float(tactic.split("~")[1])
                if tactic[0] == "a":
                    control.mouse_press()
                    time.sleep(click_time)
                    control.mouse_release()
                else:
                    control.key_press(tactic[0])
                    time.sleep(click_time)
                    control.key_release(tactic[0])
            elif '(' in tactic and ')' in tactic:  # 以设置的连续按键时间进行连续按键
                continuous_tap_time = float(tactic[tactic.find('(') + 1:tactic.find(')')])
                tap_start_time = time.time()
                while time.time() - tap_start_time < continuous_tap_time:
                    if tactic[0] == "a":
                        control.fight_click()
                    elif tactic[0] == "s":
                        control.fight_space()
                    else:
                        control.fight_tap(tactic[0])
                if tactic[0] == "r":
                    time.sleep(0.5)
                    if check_ult():
                        tactic_ult_flag = True
                        current_tactic_step = 0
                        return
            else:
                logger("释放技能失败，请检查连招格式", "WARN")
    current_tactic_step += 1
    if current_tactic_step >= len(tactics):
        current_tactic_step = 0
        if tactic_ult_flag:
            tactic_ult_flag = False
            logger("大招连段结束", "DEBUG")
        last_tactic_index = current_tactic_index
        current_tactic_index += 1
        if current_tactic_index >= len(config.FightTactics):
            current_tactic_index = 0


# 将过长的连续按键拆分为多个短的连续按键
def split_tactics(tactics):
    split_tactics_ = []
    for tactic in tactics:
        if '(' in tactic and ')' in tactic:
            action = tactic[0]
            duration = float(tactic[tactic.find('(') + 1:tactic.find(')')])
            while duration > 0.3:
                split_tactics_.append(f"{action}(0.3)")
                duration -= 0.3
            if duration > 0:
                split_tactics_.append(f"{action}({duration})")
        else:
            split_tactics_.append(tactic)
    return split_tactics_


def leaving_battle():
    for i in range(3):
        interactive()
        time.sleep(1)
    control.esc()
    time.sleep(1)


def forward():
    control.key_press("w")
    time.sleep(0.1)
    control.key_release("w")


def transfer_to_boss(bossName):
    coordinate = find_pic(template_name=f"残象探寻.png", threshold=0.5)
    if not coordinate:
        logger("识别残像探寻失败", "WARN")
        control.esc()
        return False
    click_position(coordinate)  # 进入残像探寻
    if not wait_text("探测"):
        logger("未进入残象探寻", "WARN")
        control.esc()
        return False
    logger(f"当前目标boss：{bossName}")
    findBoss = None
    y = 133
    while y < 907:
        y = y + 30
        if y > 907:
            y = 907
        findBoss = find_text(bossName)
        if findBoss:
            break
        # control.click(855 * width_ratio, y * height_ratio)
        random_click(855, y, 1, 3)
        time.sleep(0.3)
    if not findBoss:
        control.esc()
        logger("未找到目标boss", "WARN")
        return False
    click_position(findBoss.position)
    click_position(findBoss.position)
    time.sleep(1)
    # control.click(1700 * width_ratio, 980 * height_ratio)
    random_click(1700, 980)
    if not wait_text("追踪"):
        logger("未找到追踪", "WARN")
        control.esc()
        return False
    # control.click(960 * width_ratio, 540 * height_ratio)
    random_click(960, 540)
    beacon = wait_text("借位信标")
    if not beacon:
        logger("未找到借位信标", "WARN")
        control.esc()
        return False
    click_position(beacon.position)
    if transfer := wait_text("快速旅行"):
        click_position(transfer.position)
        logger("等待传送完成")
        check_loading(reload_search_model=True)
        while check_in_animation() != "is available":
            time.sleep(0.5)
        # wait_home()  # 等待回到主界面
        logger("传送完成")
        now = datetime.now()
        info.idleTime = now  # 重置空闲时间
        info.lastFightTime = now  # 重置最近检测到战斗时间
        info.fightTime = now  # 重置战斗时间
        info.lastBossName = bossName
        info.waitBoss = True
        return True
    control.esc()
    return False


def transfer_to_dreamless():
    coordinate = find_pic(template_name="周期挑战.png", threshold=0.5)
    if not coordinate:
        logger("识别周期挑战失败", "WARN")
        control.esc()
        return False
    click_position(coordinate)  # 进入周期挑战
    if not wait_text("前往"):
        logger("未进入周期挑战", "WARN")
        control.esc()
        return False
    logger(f"当前目标boss：无妄者")
    time.sleep(2)
    findBoss = find_text("战歌")
    if not findBoss:
        control.esc()
        logger("未找到战歌重奏")
        return False
    click_position(findBoss.position)
    click_position(findBoss.position)
    time.sleep(1)
    random_click(1720, 460)
    # control.click(1720 * width_ratio, 420 * height_ratio)
    if transfer := wait_text("快速旅行"):
        click_position(transfer.position)
        logger("等待传送完成")
        time.sleep(1)
        check_loading()
        while check_in_animation() != "is available":
            time.sleep(0.5)
        # wait_home()  # 等待回到主界面
        logger("传送完成")
        time.sleep(2)
        now = datetime.now()
        info.idleTime = now  # 重置空闲时间
        info.lastFightTime = now  # 重置最近检测到战斗时间
        info.fightTime = now  # 重置战斗时间
        for i in range(5):
            forward()
            time.sleep(0.1)
        return True
    logger("未找到快速旅行", "WARN")
    control.esc()
    return False


def transfer() -> bool:
    # if config.CharacterHeal:
    while check_in_animation() != "is available":
        control.esc()
        time.sleep(1)
        info.actionErrorTimes = 0
    check_heal()
    if change_task_to_synthesis():
        return True
    if info.fightTime:
        check_fight_time(info.lastBossName)
    if config.UseConsumables and config.ConsumablesName:
        use_consumable()
    if not info.needHeal:  # 检查是否需要治疗
        logger("无需治疗")
    else:
        # healBossName = "朔雷之鳞"  # 固定目标boss名称
        logger("开始治疗")
        time.sleep(1)
        info.lastBossName = "治疗"
        control.activate()
        time.sleep(0.5)
        control.tap(win32con.VK_F2)
        time.sleep(1)
        transfer_to_heal()
        return False
    bossName = config.TargetBoss[info.bossIndex % len(config.TargetBoss)]
    check_boss(bossName)
    if info.lastBossName == "无妄者" and bossName == "无妄者":
        logger("前往无妄者 且 刚才已经前往过")
        if load_special_code(bossName):
            logger(f"使用了【{bossName}】的特殊进图代码", "DEBUG")
            pass
        else:
            logger(f"未检测到【{bossName}】的特殊进图代码，常规进图", "DEBUG")
            for i in range(15):
                forward()
                time.sleep(0.1)
        now = datetime.now()
        info.idleTime = now  # 重置空闲时间
        info.lastFightTime = now  # 重置最近检测到战斗时间
        info.fightTime = now  # 重置战斗时间
        info.lastBossName = ""
        info.lastBossIndex = info.bossIndex
        info.bossIndex += 1
        return True
    if info.lastBossName == "角" and bossName == "角":
        logger("前往角 且 刚才已经前往过")
        if load_special_code(bossName):
            logger(f"使用了【{bossName}】的特殊进图代码", "DEBUG")
            pass
        else:
            logger(f"未检测到【{bossName}】的特殊进图代码，常规进图", "DEBUG")
            control.tap("s")
            time.sleep(0.5)
            control.mouse_middle()
            time.sleep(0.5)
            control.tap("d")
            control.tap("d")
            for i in range(5):
                forward()
                time.sleep(0.1)
        now = datetime.now()
        info.idleTime = now  # 重置空闲时间
        info.lastFightTime = now  # 重置最近检测到战斗时间
        info.fightTime = now  # 重置战斗时间
        info.lastBossName = ""
        info.lastBossIndex = info.bossIndex
        info.bossIndex += 1
        return True
    control.activate()
    time.sleep(0.5)
    control.tap(win32con.VK_F2)
    time.sleep(0.5)
    if not wait_text(
            ["日志", "活跃", "挑战", "强者", "残象", "周期", "探寻", "漂泊"], timeout=5
    ):
        logger("未进入索拉指南", "WARN")
        control.esc()
        info.lastFightTime = datetime.now()
        return False
    time.sleep(1)
    if info.needHeal:
        transfer_to_heal()
    elif bossName == "无妄者":
        info.lastBossIndex = info.bossIndex
        info.bossIndex += 1
        return transfer_to_dreamless()
    else:
        info.lastBossIndex = info.bossIndex
        info.bossIndex += 1
        return transfer_to_boss(bossName)


def screenshot() -> np.ndarray | None:
    """
    截取当前窗口的屏幕图像。

    通过调用Windows图形设备接口（GDI）和Python的win32gui、win32ui模块，
    本函数截取指定窗口的图像，并将其存储为numpy数组。

    返回值:
        - np.ndarray: 截图的numpy数组，格式为RGB（不包含alpha通道）。
        - None: 如果截取屏幕失败，则返回None。
    """
    hwndDC = win32gui.GetWindowDC(hwnd)  # 获取窗口设备上下文（DC）
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)  # 创建MFC DC从hwndDC
    saveDC = mfcDC.CreateCompatibleDC()  # 创建与mfcDC兼容的DC
    saveBitMap = win32ui.CreateBitmap()  # 创建一个位图对象
    saveBitMap.CreateCompatibleBitmap(mfcDC, real_w, real_h)  # 创建与mfcDC兼容的位图
    saveDC.SelectObject(saveBitMap)  # 选择saveDC的位图对象，准备绘图

    # 尝试使用PrintWindow函数截取窗口图像
    result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)
    if result != 1:
        config.RebootCount += 1
        logger(
            "截取游戏窗口失败，请勿最小化窗口，已重试："
            + str(config.RebootCount)
            + "次",
            "ERROR",
        )
        # 释放所有资源
        try:
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
            del hwndDC, mfcDC, saveDC, saveBitMap
        except Exception as e:
            logger(f"清理截图资源失败: {e}", "ERROR")
        # 重试，若失败多次重新启动游戏以唤醒至前台
        if config.RebootCount < 5:
            time.sleep(1)
            return screenshot()  # 截取失败，重试
        else:
            config.RebootCount = 0
            logger("正在重新启动游戏及脚本...", "INFO")
            from main import close_window
            close_window()
            # close_window("UnrealWindow", "鸣潮  ")
            raise Exception("截取游戏窗口失败且重试次数超过上限，正在重启游戏") from None

    # 从位图中获取图像数据
    bmp_info = saveBitMap.GetInfo()  # 获取位图信息
    bmp_str = saveBitMap.GetBitmapBits(True)  # 获取位图数据
    im = np.frombuffer(bmp_str, dtype="uint8")  # 将位图数据转换为numpy数组
    im.shape = (bmp_info["bmHeight"], bmp_info["bmWidth"], 4)  # 设置数组形状
    # 调整通道顺序 并 去除alpha通道
    im = im[:, :, [2, 1, 0, 3]][:, :, :3]

    # 清理资源
    try:
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)
    except Exception as e:
        logger(f"清理截图资源失败: {e}", "ERROR")
    return im  # 返回截取到的图像


rare_chars = "鸷"


def search_text(results: List[OcrResult], target: str) -> OcrResult | None:
    target = re.sub(
        rf"[{rare_chars}]", ".", target
    )  # 判断 target 是否包含生僻字，如果包含则使用正则将生僻字替换为任意字符
    for result in results:
        if re.search(target, result.text):  # 使用正则匹配
            return result
    return None


def find_text(targets: str | list[str]) -> OcrResult | None:
    if isinstance(targets, str):
        targets = [targets]
    img = screenshot()
    if img is None:
        return None
    result = ocr(img)
    for target in targets:
        if text_info := search_text(result, target):
            return text_info
    return None


def wait_text(targets: str | list[str], timeout: int = 3) -> OcrResult | None:
    start = datetime.now()
    if isinstance(targets, str):
        targets = [targets]
    while True:
        now = datetime.now()
        if (now - start).seconds > timeout:
            return None

        img = screenshot()
        if img is None:
            time.sleep(0.1)  # 如果截图失败，等待短暂时间再试
            continue

        result = ocr(img)
        for target in targets:
            if text_info := search_text(result, target):
                return text_info

        time.sleep(0.1)  # 每次截图和 OCR 处理之间增加一个短暂的暂停时间
    return None


def wait_home(timeout=120):
    """
    等待回到主界面
    :param timeout:  超时时间
    :return:
    """
    start = datetime.now()
    while True:
        # 修复部分情况下导致无法退出该循环的问题。
        if (datetime.now() - start).seconds > timeout:
            return None
        img = screenshot()
        if img is None:
            continue
        results = ocr(img)
        if text_info := search_text(results, "特征码"):  # 特征码
            return text_info
        template = Image.open(os.path.join(root_path, r"template/背包.png"))  # 背包
        template = np.array(template)
        if match_template(img, template, threshold=0.9):
            return
        template = Image.open(
            os.path.join(root_path, r"template/终端按钮.png")
        )  # 终端按钮
        template = np.array(template)
        if match_template(img, template, threshold=0.9):
            return


def turn_to_search(turn_times) -> int | None:
    x = None
    if turn_times == 1:
        control.activate()
        control.mouse_middle()  # 重置视角
        for _ in range(3):
            if absorption_and_receive_rewards({}):
                info.needAbsorption = False
                info.searchTimes = 0
                break
            control.key_press("w")
            time.sleep(0.1)
            control.key_release("w")
            img = screenshot()
            x = search_echoes(img)
            if x:
                break
        time.sleep(1)
        return x
    else:
        logger("转动视角")
        control.tap("a")
        time.sleep(0.3)
        control.mouse_middle()
        time.sleep(1)
    img = screenshot()
    x = search_echoes(img)
    if x is None:
        logger("未发现声骸")
    return x


def absorption_action():
    info.searchTimes += 1
    if info.searchTimes == 1:
        info.searchStartTime = datetime.now()  # 开始时间
        # if config.CharacterHeal:
        info.checkHeal = True
    absorption_max_time = (
        config.MaxEchoAbsorptionTime if config.MaxEchoAbsorptionTime > 5 else 5
    )
    if (datetime.now() - info.searchStartTime).seconds < absorption_max_time:  # 未超过最大吸收时间
        x = turn_to_search(info.searchTimes)
        if x is None:
            if absorption_and_receive_rewards({}):
                info.needAbsorption = False
                info.searchTimes = 0
            return
        last_x = None
        while (
                datetime.now() - info.searchStartTime
        ).seconds < absorption_max_time:  # 未超过最大吸收时间
            img = screenshot()
            x = search_echoes(img)
            if x is None and last_x is None:
                break
            if x is None:
                info.searchTimes += 1
                temp_x = turn_to_search(info.searchTimes)
                x = temp_x if temp_x else last_x  # 如果未发现声骸，使用上一次的x坐标
            last_x = x
            center_x = real_w // 2
            floating = real_w // 20
            if x < center_x - floating:
                logger("发现声骸 向左移动")
                control.tap("a")
            elif x > center_x + floating:
                logger("发现声骸 向右移动")
                control.tap("d")
            else:
                logger("发现声骸 向前移动")
                control.tap("w")
            if absorption_and_receive_rewards({}):
                info.needAbsorption = False
                info.searchTimes = 0
                break
    else:
        info.needAbsorption = False
        info.searchTimes = 0
        return
    if (datetime.now() - info.searchStartTime).seconds >= absorption_max_time:
        info.needAbsorption = False
        info.searchTimes = 0


def absorption_and_receive_rewards(positions: dict[str, Position]) -> bool:
    """
    吸收和领取奖励重合
    :param positions: 位置信息
    :return:
    """
    control.activate()
    count = 0
    while find_text("吸收"):
        if count % 2:
            logger("向下滚动后尝试吸收")
            control.scroll(-1)
            time.sleep(1)
        count += 1
        interactive()
        time.sleep(2)
        if find_text("确认"):
            logger("点击到领取奖励，关闭页面")
            control.esc()
            time.sleep(2)
    if count == 0:
        absorption_max_time = (
            config.MaxEchoAbsorptionTime if config.MaxEchoAbsorptionTime > 5 else 5
        )
        if (datetime.now() - info.searchStartTime).seconds >= absorption_max_time:
            info.needAbsorption = False
            info.searchTimes = 0
        return False
    logger("吸收声骸")
    info.absorptionCount += 1
    boss_index = info.lastBossIndex % len(config.TargetBoss)
    info.bossAllEchoAbsorptionTimes[boss_index] += 1
    check_echo_is_over()
    info.lastFightTime = info.lastFightTime - timedelta(seconds=(config.MaxIdleTime + 5))  # 吸收完成后立即结束等待
    return True


def transfer_to_heal(healBossName: str = "朔雷之鳞"):
    """
    如果需要治疗，传送到固定位置进行治疗。
    """
    coordinate = find_pic(template_name="残象探寻.png", threshold=0.5)
    if not coordinate:
        logger("识别残像探寻失败", "WARN")
        control.esc()
        return False
    click_position(coordinate)  # 进入残像探寻
    if not wait_text("探测"):
        logger("未进入残象探寻", "WARN")
        control.esc()
        return False
    findBoss = None
    y = 133
    while y < 907:
        y = y + 30
        if y > 907:
            y = 907
        findBoss = find_text(healBossName)
        if findBoss:
            break
        # control.click(855 * width_ratio, y * height_ratio)
        random_click(855, y)
        time.sleep(0.3)
    if not findBoss:
        control.esc()
        logger("治疗_未找到神像附近点位BOSS(朔雷之鳞)", "WARN")
        return False
    click_position(findBoss.position)
    click_position(findBoss.position)
    time.sleep(1)
    # control.click(1700 * width_ratio, 980 * height_ratio)
    random_click(1700, 980)
    if not wait_text("追踪"):
        logger("治疗_未找到追踪", "WARN")
        control.esc()
        return False
    region = set_region(1625, 895, 1885, 1050)
    if info.healCount == 0:  # 首次进行治疗的时候先进行地图缩放
        i = 0
        while not wait_text_designated_area("自定义标记", region=region):
            random_click(960, 300)
            time.sleep(0.5)
            i += 1
            if i > 3:
                for _ in range(2):
                    control.esc()
                    time.sleep(0.5)
                logger("地图缩放时出现问题，退出地图界面")
                return
        for _ in range(5):
            control.scroll(3, 960 * width_ratio, 540 * height_ratio)
            time.sleep(0.2)
            logger("正在对地图进行缩放")
        time.sleep(0.5)
    # control.click(1210 * width_ratio, 525 * height_ratio)
    random_click(1210, 525)
    if transfer := wait_text("快速旅行"):
        click_position(transfer.position)
        logger("治疗_等待传送完成")
        time.sleep(1)
        check_loading()
        while check_in_animation() != "is available":
            time.sleep(0.5)
        # wait_home()  # 等待回到主界面
        logger("治疗_传送完成")
        info.characterHealthyIndex = [True, True, True, True]
        now = datetime.now()
        info.idleTime = now  # 重置空闲时间
        info.lastFightTime = now  # 重置最近检测到战斗时间
        info.fightTime = now  # 重置战斗时间
        info.needHeal = False
        info.healCount += 1
        info.lastFightTime = info.lastFightTime - timedelta(seconds=(config.MaxIdleTime + 5))  # 治疗后立即传送
        return True
    control.esc()
    return False


def equip_consumable():
    # info.consumablesInfo[]说明：
    # [0]：消耗品ID
    # [1]：消耗品名称
    # [2]：消耗品类型
    # [3]：消耗品效果描述
    # [4]：消耗品持续时间(秒)
    # [5]：消耗品图片Path
    # [6]：消耗品数量
    if config.UseConsumables and config.ConsumablesName:
        consumables_name = config.ConsumablesName
        info.consumablesInfo = consumables.get_consumables_info(consumables_name)
        if info.consumablesInfo:
            # 检查背包内有无该物品
            while check_in_animation() != "is available":
                logger(f"检查背包有无消耗品 【{info.consumablesInfo[1]}】")
                control.esc()
                time.sleep(1)
            control.esc()
            time.sleep(1)
            for _ in range(3):
                random_click(1794, 527)
                time.sleep(0.2)
            time.sleep(1)
            random_click(1671, 212)
            time.sleep(1)
            random_click(400, 800)
            time.sleep(0.5)
            coordinate = find_text("补给品").position
            click_position(coordinate)
            time.sleep(0.5)
            i = 0
            for _ in range(3):
                control.click(1840 * width_ratio, 198 * height_ratio)
                time.sleep(0.2)
            while not find_pic(1310, 160, 1890, 890, info.consumablesInfo[5], 0.85, need_resize=True, tmp_is_transparent_background=True):
                # 滚动背包
                if i > 120:
                    logger(f"未找到消耗品 【{info.consumablesInfo[1]}】", "DEBUG")
                    info.consumablesInfo.append(0)
                    time.sleep(0.5)
                    control.esc()
                    time.sleep(0.5)
                    control.esc()
                    time.sleep(1.5)
                    while check_in_animation() != "is available":
                        control.esc()
                        time.sleep(1)
                    time.sleep(1)
                    return False
                control.scroll(count=-3, x=1490 * width_ratio, y=390 * height_ratio)
                i += 1
                time.sleep(0.1)
            coords = find_pic(1310, 160, 1890, 890, info.consumablesInfo[5], 0.85, need_resize=True, tmp_is_transparent_background=True)
            center_x = int((coords.x1 + coords.x2) / 2)
            center_y = int((coords.y1 + coords.y2) / 2)
            random_click(center_x, center_y, ratio=False)
            if find_text("装配"):
                coordinate = find_text("装配").position
                click_position(coordinate)
                logger(f"消耗品 【{info.consumablesInfo[1]}】 装备成功，切换探索模块", "DEBUG")
            else:
                logger(f"消耗品 【{info.consumablesInfo[1]}】 已经装备", "DEBUG")
            time.sleep(0.5)
            control.esc()
            time.sleep(0.5)
            control.esc()
            time.sleep(1.5)
            while check_in_animation() != "is available":
                control.esc()
                time.sleep(1)
            time.sleep(1)
            region = set_region(901, 751, 1045, 860)
            control.key_press(win32con.VK_TAB)
            time.sleep(1.5)
            text_result = wait_text_designated_area("", 1, region, 3, full_text_return=True)
            if text_result and text_result[0].text != "":
                consumable_quantity = re.sub(r'\D', '', text_result[0].text)  # 只提取识别出的字符的数字部分
                info.consumablesInfo.append(int(consumable_quantity))
            else:
                logger(f"无法识别到 【{info.consumablesInfo[1]}】 剩余个数", "DEBUG")
                info.consumablesInfo.append(0)
            random_click(957, 800)
            time.sleep(0.5)
            control.key_release(win32con.VK_TAB)
            try:
                consumable_quantity = info.consumablesInfo[6]
                logger(f"切换探索模块成功，【{info.consumablesInfo[1]}】剩余个数：【{info.consumablesInfo[6]}】", "DEBUG")
            except IndexError:
                logger(f"切换探索模块失败","DEBUG")
        else:
            logger(f"游戏中没有名称为 {consumables_name} 的消耗品", "DEBUG")
    else:
        logger(f"未设置消耗品", "DEBUG")


def use_consumable():
    # info.consumablesInfo[]说明：
    # [0]：消耗品ID
    # [1]：消耗品名称
    # [2]：消耗品类型
    # [3]：消耗品效果描述
    # [4]：消耗品持续时间(秒)
    # [5]：消耗品图片Path
    # [6]：消耗品数量
    # 当消耗品数量大于0，且消耗品持续时间大于0(防止连续使用生命药水等没有持续时间的消耗品)，且消耗品BUFF结束时间小于当前时间时，使用消耗品
    i = 0
    if config.UseConsumables and config.ConsumablesName:
        if info.consumablesInfo[6] > 0:
            if info.consumablesInfo[4] != 0:
                if datetime.now() > info.consumablesEndTime:
                    while check_in_animation() != "is available":
                        if i > 5:
                            logger(f"状态异常无法使用【{info.consumablesInfo[1]}】","DEBUG")
                            break
                        i += 1
                        time.sleep(0.3)
                    if check_in_animation() == "is available":
                        control.tap("t")
                        info.consumablesInfo[6] -= 1
                        logger(f"使用了【{info.consumablesInfo[1]}】，剩余个数：【{info.consumablesInfo[6]}】", "DEBUG")
                        info.consumablesEndTime = datetime.now() + timedelta(seconds=info.consumablesInfo[4])
                        end_time_message = info.consumablesEndTime.strftime("%Y年%m月%d日 %H:%M:%S")
                        logger(f"下次将在【{end_time_message}】后使用", "DEBUG")
                    else:
                         logger(f"【{info.consumablesInfo[1]}】使用失败","DEBUG")
                else:
                    logger(f"【{info.consumablesInfo[1]}】尚在持续时间内，未使用消耗品", "DEBUG")
            else:
                logger(f"【{info.consumablesInfo[1]}】使用条件不满足，未使用消耗品", "DEBUG")
        else:
            logger(f"【{info.consumablesInfo[1]}】数量不足，无法使用消耗品", "DEBUG")
    else:
        logger(f"未设置消耗品或未打开使用消耗品功能，不使用消耗品", "DEBUG")
    # if info.consumablesInfo[6] > 0 and info.consumablesInfo[4] != 0 and datetime.now() > info.consumablesEndTime:
    #     control.tap("t")
    #     info.consumablesInfo[6] -= 1
    #     logger(f"使用了【{info.consumablesInfo[1]}】，剩余个数：【{info.consumablesInfo[6]}】", " DEBUG")
    #     info.consumablesEndTime = datetime.now() + timedelta(seconds=info.consumablesInfo[4])
    #     logger(f"下次将在【{info.consumablesEndTime}】后使用")
    # else:
    #     logger(f"【{info.consumablesInfo[1]}】数量不足或尚在持续时间内，或不满足使用条件，未使用消耗品", "DEBUG")


def check_heal():
    if datetime.now() - info.startTime > timedelta(minutes=1):
        info.checkHeal = False   # 1.1.3版本更新后，仅在启动时进行检测，战斗后不再使用此函数进行判断，战斗时如有弹框，则会进行治疗
    if info.checkHeal:
        equip_consumable()  # 装备消耗品
        logger(f"正在检查角色是否需要复苏。")
        for i in range(3):
            if info.needHeal:
                break
            now = datetime.now()
            info.lastSelectRoleTime = now
            info.roleIndex += 1
            if info.roleIndex > 3:
                info.roleIndex = 1
            control.tap(str(info.roleIndex))
            region = set_region(325, 190, 690, 330)
            if not wait_text_designated_area("复苏", timeout=3, region=region):
                logger(f"{info.roleIndex}号角色无需复苏")
                info.needHeal = False
                time.sleep(0.5)
            else:
                logger(f"{info.roleIndex}号角色需要复苏")
                info.needHeal = True
                time.sleep(0.5)
                control.esc()
        info.checkHeal = False


def wait_text_designated_area(targets: str | list[str], timeout: int = 1, region: tuple = None, max_attempts: int = 3, full_text_return: bool = False, img: np.ndarray = None):
    start = datetime.now()
    if isinstance(targets, str):
        targets = [targets]

    attempt_count = 0
    while attempt_count < max_attempts:
        now = datetime.now()
        if (now - start).seconds > timeout:
            return None
        if img is None:
            img = screenshot()
        if img is None:
            time.sleep(0.1)  # 如果截图失败，等待短暂时间再试
            continue

        # 调试输出图像尺寸
        # print(f"Original image size: {img.shape}")

        # 将NumPy数组转换为Pillow图像对象
        img_pil = Image.fromarray(img)

        # 如果提供了具体的坐标区域，则裁剪图像
        if region:
            # 将坐标区域转换为整数
            region = tuple(map(int, region))
            # 调试输出裁剪区域
            # print(f"Cropping region: {region}")
            img_pil = img_pil.crop(region)

        # 将裁剪后的 Pillow 图像对象转换回 NumPy 数组
        img_cropped = np.array(img_pil)

        result = ocr(img_cropped)
        if full_text_return:
            return result

        for target in targets:
            if text_info := search_text(result, target):
                return text_info

        attempt_count += 1
        time.sleep(0.1)  # 每次截图和 OCR 处理之间增加一个短暂的暂停时间

    return None


# 计算颜色之间的欧氏距离
def color_distance(color1, color2):
    return np.linalg.norm(np.array(color1) - np.array(color2))


# 截图进行单点的颜色判断
def contrast_colors(
    coordinates: Union[Tuple[int, int], List[Tuple[int, int]]],
    target_colors: Union[Tuple[int, int, int], List[Tuple[int, int, int]]],
    threshold: float = 0.95,
    return_all: bool = False, img: np.ndarray = None
) -> Union[bool, List[bool]]:
    """
    在 (x, y) 提取颜色，并与传入颜色元组进行欧氏距离对比获取相似度，并判断 。

    :param coordinates: 坐标 (x, y) 或坐标列表 [(x1, y1), (x2, y2), ...]
    :param target_colors: 目标颜色元组 (R, G, B) 或目标颜色元组列表 [(R1, G1, B1), (R2, G2, B2), ...]
    :param threshold: 相似度阈值
    :param return_all: 是否返回所有布尔值结果列表，如果为 False 则返回单个布尔值
    :param img 如已截图，可直接使用
    :return: 如果 return_all 为 True，则返回布尔值列表；否则返回单个布尔值
    """
    # 如果传入的是单个坐标和颜色，将它们转换为列表
    if isinstance(coordinates, tuple) and isinstance(target_colors, tuple):
        coordinates = [coordinates]
        target_colors = [target_colors]

    if len(coordinates) != len(target_colors):
        if len(target_colors) == 1:
            target_colors = target_colors * len(coordinates)
        else:
            raise ValueError("坐标和颜色的数量必须相同")

    # 获取截图
    if img is None:
        img = screenshot()

    # 将 numpy 数组转换为 PIL.Image 对象
    img = Image.fromarray(img)

    results = []
    for (x, y), target_color in zip(coordinates, target_colors):
        if x is None or y is None:
            logger("传入坐标错误", "WARN")
            results.append(False)
            continue

        # 计算实际坐标
        coord = (int(x * width_ratio), int(y * height_ratio))
        # print(f"坐标为{coord}")
        # 获取指定坐标的颜色
        color = img.getpixel(coord)
        # print(f"颜色为{color}")

        # 对比颜色与参考颜色，并计算相似度
        distance = color_distance(color, target_color)
        similarity = 1 - (distance / np.linalg.norm(np.array(target_color)))

        results.append(similarity >= threshold)

        if not return_all and similarity >= threshold:
            return True

    return results if return_all else any(results)


def random_click(
        x: int = None,
        y: int = None,
        range_x: int = 3,
        range_y: int = 3,
        ratio: bool = True,
        need_print: bool = False
):
    """
    在以 (x, y) 为中心的区域内随机选择一个点并模拟点击。

    :param x: 中心点的 x 坐标
    :param y: 中心点的 y 坐标
    :param range_x: 水平方向随机偏移的范围
    :param range_y: 垂直方向随机偏移的范围
    :param ratio: 是否将坐标进行缩放
    :param need_print: 是否输出log，debug用
    """
    if x is None or y is None:
        logger("没有传入坐标，无法点击", "WARN")
    else:
        random_x = x + np.random.uniform(-range_x, range_x)
        random_y = y + np.random.uniform(-range_y, range_y)

        # 将浮点数坐标转换为整数像素坐标
        if ratio:
            # 需要缩放
            random_x = int(random_x) * width_ratio
            random_y = int(random_y) * height_ratio
        else:
            # 不需要缩放
            random_x = int(random_x)
            random_y = int(random_y)

        # 点击
        time.sleep(np.random.uniform(0, 0.1))  # 随机等待后点击
        control.click(random_x, random_y)

        if need_print:
            logger(f"点击了坐标{random_x},{random_y}", "DEBUG")
        # logger(f"点击了坐标{random_x},{random_y}")


def check_boss(bossName, is_wait: bool = False):
    """
    根据boss名称判断是否需要等待boss起身

    :param bossName: boss名称
    :param is_wait: 是否需要等待
    """
    bossName = bossName.lower()  # 将bossName转换为小写
    info.resetRole = True

    keywords_turtle = ["鸣", "钟", "之", "龟"]
    keywords_robot = ["聚", "械", "机", "偶"]
    keywords_dreamless = ["无", "妄", "者"]
    keywords_jue = ["角"]
    info.bossTrueName = bossName

    def contains_any_combinations(name, keywords, min_chars):  # 为了防止BOSS名重复，添加了最小匹配关键字数
        for r in range(min_chars, len(keywords) + 1):
            for comb in itertools.combinations(keywords, r):
                if all(word in name for word in comb):
                    return True
        return False
    if contains_any_combinations(bossName, keywords_turtle, min_chars=2):
        info.bossTrueName = "鸣钟之龟"
        info.echoSearchModel = "yolo.onnx"
        wait_time = 16
    elif contains_any_combinations(bossName, keywords_robot, min_chars=2):
        info.bossTrueName = "聚械机偶"
        info.echoSearchModel = "yolo.onnx"
        wait_time = 7
    elif contains_any_combinations(bossName, keywords_dreamless, min_chars=3):
        info.bossTrueName = "无妄者"
        info.echoSearchModel = "heart.onnx"
        wait_time = 3
        info.inDungeon = True
    elif contains_any_combinations(bossName, keywords_jue, min_chars=1):
        info.bossTrueName = "角"
        info.echoSearchModel = "jue.onnx"
        wait_time = 3
        info.inDungeon = True
    else:
        info.bossTrueName = bossName
        info.echoSearchModel = "yolo.onnx"
        wait_time = 0

    if is_wait:
        time.sleep(wait_time)
        if wait_time != 0:
            logger(f"{info.bossTrueName}需要等待{wait_time}秒开始战斗！", "DEBUG")
        else:
            logger("当前BOSS不需要等待，直接开始战斗！", "DEBUG")
        info.waitBoss = False
    else:
        logger(f"即将前往{info.bossTrueName}")


def set_region(x_upper_left: int = None, y_upper_left: int = None, x_lower_right: int = None,
               y_lower_right: int = None):
    """
    设置区域的坐标并将其缩放到特定比例。

    :param x_upper_left: 左上角的 x 坐标。
    :param y_upper_left: 左上角的 y 坐标。
    :param x_lower_right: 右下角的 x 坐标。
    :param y_lower_right: 右下角的 y 坐标。

    返回:
    tuple or bool: 如果所有坐标参数都提供，返回缩放后的坐标元组 (x_upper_left_scaled, y_upper_left_scaled,
                   x_lower_right_scaled, y_lower_right_scaled)。
                   如果有任何坐标参数未提供，返回 False。

    """
    if None in [x_upper_left, y_upper_left, x_lower_right, y_lower_right]:
        logger("set_region error:传入坐标参数不正确", "WARN")
        return False
    region = (
        x_upper_left * width_ratio,
        y_upper_left * height_ratio,
        x_lower_right * width_ratio,
        y_lower_right * height_ratio
    )
    region = tuple(map(int, region))
    return region


def echo_bag_lock():
    """
    声骸锁定
    目前只支持背包锁定，暂不支持合成时判断
    """
    # 开始执行判断
    if not config.EchoLock:
        logger("未启动该功能", "WARN")
        return False
    info.echoNumber += 1
    this_echo_row = info.echoNumber // 6 + 1
    this_echo_col = info.echoNumber % 6
    if this_echo_col == 0:
        this_echo_col = 6
        this_echo_row -= 1
    if info.echoNumber == 1:
        logger("检测到声骸背包画面，3秒后将开始执行锁定程序，过程中请不要将鼠标移到游戏内。", "DEBUG")
        logger("tips:此功能需要关闭声骸详细描述(在角色声骸装备处打开简介这里是详情，关闭简介这里是简介，反着的)", "WARN")
        time.sleep(3)
        # 切换到时间顺序(倒序)
        logger("切换为时间倒序")
        random_click(400, 980)
        time.sleep(1)
        random_click(400, 845)
        time.sleep(0.5)
        random_click(718, 23)
        time.sleep(0.5)
    if config.EchoDebugMode:
        logger(f"当前为第{this_echo_row}排，第{this_echo_col}个声骸 (总第{info.echoNumber}个)", "DEBUG")
    echo_start_position = [285, 205]  # 第一个声骸的坐标
    echo_spacing = [165, 205]  # 两个声骸间的间距
    this_echo_x_position = (this_echo_col - 1) * echo_spacing[0] + echo_start_position[0]  # 当前需要判断的声骸x坐标
    random_click(this_echo_x_position, echo_start_position[1])  # 选择当前声骸
    time.sleep(0.3)

    # 判断声骸是否为金色品质，如果不是则返回
    check_point = (1704, 393)
    if not contrast_colors(check_point, (255, 255, 255)):
        if config.EchoDebugMode:
            logger("当前声骸不是金色声骸，下一个", "DEBUG")
        echo_next_row(info.echoNumber)
        return True
    # 判断当前声骸是否未锁定
    img = screenshot()
    coordinate_lock = find_pic(1700, 270, 1850, 395, f"声骸锁定{info.adaptsResolution}.png", 0.98, img, False)
    coordinate_unlock = find_pic(1700, 270, 1850, 395, f"声骸未锁定{info.adaptsResolution}.png", 0.98, img, False)
    if coordinate_lock:
        lock_position = coordinate_lock
        info.echoIsLockQuantity += 1
        if config.EchoDebugMode:
            logger("当前声骸已锁定", "DEBUG")
        if info.echoIsLockQuantity > config.EchoMaxContinuousLockQuantity:
            logger(f"连续检出已锁定声骸{info.echoIsLockQuantity}个，超出设定值，结束", "DEBUG")
            logger(f"本次总共检查{info.echoNumber}个声骸，有{info.inSpecEchoQuantity}符合条件并锁定！！")
            this_echo_lock = True
            return False
        echo_next_row(info.echoNumber)
        return True
    # elif contrast_colors((1812, 328), (36, 35, 11), 0.6):
    elif coordinate_unlock:
        lock_position = coordinate_unlock
        this_echo_lock = False
        info.echoIsLockQuantity = 0
        if config.EchoDebugMode:
            logger("当前声骸未锁定", "DEBUG")
    else:
        this_echo_lock = None
        logger("未检测到当前声骸锁定状况", "WARN")
        return False

    # 识别声骸Cost
    this_echo_cost = None
    img = screenshot()
    if find_pic(1690, 200, 1830, 240, f"COST1{info.adaptsResolution}.png", 0.98, img, False):
        this_echo_cost = "1"
    if find_pic(1690, 200, 1830, 240, f"COST3{info.adaptsResolution}.png", 0.98, img, False):
        this_echo_cost = "3"
    if find_pic(1690, 200, 1830, 240, f"COST4{info.adaptsResolution}.png", 0.98, img, False):
        this_echo_cost = "4"
    if this_echo_cost is None:
        logger("未能识别到Cost","ERROR")
        return False
    if config.EchoDebugMode:
        logger(f"当前声骸Cost为{this_echo_cost}", "DEBUG")

    # 识别声骸主词条属性
    if this_echo_cost == "4":  # 4COST描述太长，可能将副词条识别为主词条
        random_click(1510, 690)
        time.sleep(0.02)
        if find_pic(1295, 465, 1360, 515, f"声骸_攻击{info.adaptsResolution}.png", 0.7, need_resize=False) is None:
            for i in range(18):
                control.scroll(1, 1510 * width_ratio, 690 * height_ratio)
                time.sleep(0.02)
            time.sleep(0.8)
            random_click(1510, 690)
    region = set_region(1425, 425, 1620, 470)
    cost_mapping = {
        "1": (echo.echoCost1MainStatus, 1),
        "3": (echo.echoCost3MainStatus, 1),
        "4": (echo.echoCost4MainStatus, 1),
    }
    if this_echo_cost in cost_mapping:
        func, param = cost_mapping[this_echo_cost]
        text_result = wait_text_designated_area(func, param, region, 3)
        this_echo_main_status = remove_non_chinese(wait_text_result_search(text_result))
        if config.EchoDebugMode:
            logger(f"当前声骸主词条为：{this_echo_main_status}", "DEBUG")
        else:
            if this_echo_main_status is False:
                text_result = wait_text_designated_area("灭伤害加成", 1, region, 3)
                if text_result:
                    this_echo_main_status = "湮灭伤害加成"
                else:
                    text_result1 = wait_text_designated_area("攻", 1, region, 3)
                    text_result2 = wait_text_designated_area("击", 1, region, 3)
                    if text_result1 or text_result2:
                        this_echo_main_status = "攻击"
            if this_echo_main_status is False:
                random_click(1510, 690)
                time.sleep(0.02)
                for i in range(18):
                    control.scroll(1, 1510 * width_ratio, 690 * height_ratio)
                    time.sleep(0.02)
                time.sleep(0.8)
                random_click(1510, 690)
                if this_echo_cost in cost_mapping:
                    func, param = cost_mapping[this_echo_cost]
                    text_result = wait_text_designated_area(func, param, region, 3)
                    this_echo_main_status = remove_non_chinese(wait_text_result_search(text_result))
                    if this_echo_main_status is False:
                        text_result = wait_text_designated_area("灭伤害加成", 1, region, 3)
                        if text_result:
                            this_echo_main_status = "湮灭伤害加成"
                        else:
                            text_result1 = remove_non_chinese(wait_text_designated_area("攻", 1, region, 3))
                            text_result2 = remove_non_chinese(wait_text_designated_area("击", 1, region, 3))
                            if text_result1 or text_result2:
                                this_echo_main_status = "攻击"
            else:
                logger(f"声骸主词条识别错误1", "ERROR")
                return False
    else:
        logger(f"声骸主词条识别错误2", "ERROR")
        return False

    # 识别声骸套装属性
    region = set_region(1295, 430, 1850, 930)
    text_result = wait_text_designated_area(echo.echoSetName, 2, region, 5)
    this_echo_set = remove_non_chinese(wait_text_result_search(text_result))
    if this_echo_set:
        if config.EchoDebugMode:
            logger(f"当前声骸的套装为：{this_echo_set}", "DEBUG")
        pass
    else:
        random_click(1510, 690)
        time.sleep(0.02)
        for i in range(18):
            control.scroll(-1, 1510 * width_ratio, 690 * height_ratio)
            time.sleep(0.02)
        time.sleep(0.8)
        random_click(1510, 690)
        text_result = wait_text_designated_area(echo.echoSetName, 2, region, 5)
        this_echo_set = remove_non_chinese(wait_text_result_search(text_result))
        if this_echo_set:
            if config.EchoDebugMode:
                logger(f"当前声骸的套装为：{this_echo_set}", "DEBUG")
            pass
        else:
            logger(f"声骸套装识别错误", "ERROR")
            return False

    # 提取声骸名称
    region = set_region(1300, 120, 1850, 170)
    text_result = wait_text_designated_area(echo.echoName, 1, region, 3)
    this_echo_name = remove_non_chinese(wait_text_result_search(text_result))
    if this_echo_name:
        this_echo_name = echo_name_check(this_echo_name)
        if config.EchoDebugMode:
            logger(f"当前声骸名称为：{this_echo_name}", "DEBUG")
        pass
    else:
        if config.EchoDebugMode:
            logger(f"识别声骸名称失败 (只影响显示，不影响正常判定)", "WARN")
        this_echo_name = "未知"
        pass

    # 声骸信息合成
    log_str = (
            "" +
            f"当前是第{info.echoNumber}个声骸" +
            f"，{this_echo_name}" +
            f"，{this_echo_cost}Cost" +
            f"，{this_echo_set}" +
            f"，{this_echo_main_status}"
    )
    # 锁定声骸，输出声骸信息
    this_echo_cost = this_echo_cost + "COST"
    if is_echo_main_status_valid(this_echo_set, this_echo_cost, this_echo_main_status, config.EchoLockConfig):
        if this_echo_lock is True:
            if config.EchoDebugMode:
                logger("当前声骸符合要求，已处于锁定状态", "DEBUG")
                # 此处无作用，因为锁定的直接跳过了，提高效率
                log_str = log_str + "，已锁定"
                logger(log_str, "DEBUG")
        else:
            if config.EchoDebugMode:
                logger(f"当前声骸符合要求，锁定声骸", "DEBUG")
            log_str = log_str + "，执行锁定"
            info.inSpecEchoQuantity += 1
            # random_click(1807, 327)
            click_position(lock_position)
            time.sleep(0.5)
            logger(log_str)
    else:
        if config.EchoDebugMode:
            logger(f"不符合，跳过", "DEBUG")
    # echo_next_row(this_echo_row)
    echo_next_row(info.echoNumber)


# def echo_next_row(this_echo_row):
def echo_next_row(echo_number):
    def scroll_and_check(min_times, max_times, message, check_condition):
        local_scroll_times = 0
        img = screenshot()
        while local_scroll_times < min_times or (local_scroll_times < max_times and not check_condition(img)):
            if config.EchoDebugMode:
                logger(message, "DEBUG")
            control.scroll(-1, 1120 * width_ratio, 210 * height_ratio)
            local_scroll_times += 1
            time.sleep(0.06)
            img = screenshot()
        return local_scroll_times

    def find_cost(img):
        for i in [1, 3, 4]:
            if find_pic(315, 220, 360, 275, f"声骸行数滑动判断用COST{i}{info.adaptsResolution}.png", 0.8, img, False):
                return True
        return False

    if echo_number % 6 == 0:
        random_click(1120, 210)

        scroll_times_out_edge = scroll_and_check(3, 6, "正在划出当前边缘", find_cost)
        if config.EchoDebugMode:
            logger(f"已划出当前边缘,滑动次数：{scroll_times_out_edge}", "DEBUG")

        scroll_times_next_edge = scroll_and_check(0, 4, "正在划到下一个边缘", lambda img: find_cost(img))
        time.sleep(0.3)

        if scroll_times_next_edge >= 4:
            if config.EchoDebugMode:
                logger("自动滑动至下一排超出尝试次数，使用默认值尝试", "WARN")
            return False
        if config.EchoDebugMode:
            logger(f"已划到下一个边缘,滑动次数：{scroll_times_next_edge}", "DEBUG")

    # 另一种行数切换的方法，需要电脑特别稳定
    # if info.echoNumber % 6 == 0:
    #     scroll_times = 7  # 默认值
    #     # logger("切换至下一排")
    #     if this_echo_row % 4 != 0 and this_echo_row % 15 != 0:
    #         scroll_times = 8  # 通常情况下滑动滚轮8次
    #     elif this_echo_row % 4 == 0 and this_echo_row % 15 != 0:
    #         scroll_times = 7  # 每4行进行一次修正
    #     elif this_echo_row % 15 == 0:
    #         scroll_times = 9  # 每15行再进行一次修正
    #     for i in range(scroll_times):
    #         control.scroll(-1, 285 * width_ratio, 205 * height_ratio)
    #         time.sleep(0.06)
    #     time.sleep(0.3)
    #     return True


def echo_synthesis():
    """
        : 声骸合成锁定功能
        : update: 2024/06/26 16:16:00
        : author: RoseRin0
    """
    def check_echo_cost():
        this_synthesis_echo_cost = None
        cost_img = screenshot()
        if find_pic(1090, 210, 1230, 255, f"合成_COST1{info.adaptsResolution}.png", 0.98, cost_img, False):
            this_synthesis_echo_cost = "1"
        if find_pic(1075, 195, 1230, 255, f"合成_COST3{info.adaptsResolution}.png", 0.98, cost_img, False):
            this_synthesis_echo_cost = "3"
        if find_pic(1075, 195, 1230, 255, f"合成_COST4{info.adaptsResolution}.png", 0.98, cost_img, False):
            this_synthesis_echo_cost = "4"
        if this_synthesis_echo_cost is None:
            logger("未能识别到Cost", "ERROR")
            return False
        if config.EchoSynthesisDebugMode:
            logger(f"当前声骸Cost为{this_synthesis_echo_cost}", "DEBUG")
        return this_synthesis_echo_cost

    def check_echo_main_status(this_synthesis_echo_cost):
        this_synthesis_echo_main_status = None
        if this_synthesis_echo_cost == "4":  # 4COST描述太长，可能将副词条识别为主词条
            random_click(1000, 685)
            time.sleep(0.02)
            if find_pic(715, 480, 760, 520, f"声骸_攻击{info.adaptsResolution}.png", 0.7, need_resize=False) is None:
                for i in range(18):
                    control.scroll(1, 1000 * width_ratio, 685 * height_ratio)
                    time.sleep(0.02)
                time.sleep(0.8)
                random_click(1000, 685)
        region = set_region(830, 440, 1250, 475)
        cost_mapping = {
            "1": (echo.echoCost1MainStatus, 1),
            "3": (echo.echoCost3MainStatus, 1),
            "4": (echo.echoCost4MainStatus, 1),
        }
        if this_synthesis_echo_cost in cost_mapping:
            func, param = cost_mapping[this_synthesis_echo_cost]
            text_result = wait_text_designated_area(func, param, region, 3)
            this_synthesis_echo_main_status = remove_non_chinese(wait_text_result_search(text_result))
            if this_synthesis_echo_main_status is False:
                text_result = wait_text_designated_area("灭伤害加成", 1, region, 3)
                if text_result:
                    this_synthesis_echo_main_status = "湮灭伤害加成"
                else:
                    text_result1 = wait_text_designated_area("攻", 1, region, 3)
                    text_result2 = wait_text_designated_area("击", 1, region, 3)
                    if text_result1 or text_result2:
                        this_synthesis_echo_main_status = "攻击"
            if this_synthesis_echo_main_status is False:
                random_click(1000, 685)
                time.sleep(0.02)
                for i in range(18):
                    control.scroll(1, 1000 * width_ratio, 685 * height_ratio)
                    time.sleep(0.02)
                time.sleep(0.8)
                random_click(1000, 685)
                if this_synthesis_echo_cost in cost_mapping:
                    func, param = cost_mapping[this_synthesis_echo_cost]
                    text_result = wait_text_designated_area(func, param, region, 3)
                    this_synthesis_echo_main_status = remove_non_chinese(wait_text_result_search(text_result))
                    if this_synthesis_echo_main_status is False:
                        text_result = wait_text_designated_area("灭伤害加成", 1, region, 3)
                        if text_result:
                            this_synthesis_echo_main_status = "湮灭伤害加成"
                        else:
                            text_result1 = wait_text_designated_area("攻", 1, region, 3)
                            text_result2 = wait_text_designated_area("击", 1, region, 3)
                            if text_result1 or text_result2:
                                this_synthesis_echo_main_status = "攻击"
            if this_synthesis_echo_main_status is False:
                    logger(f"声骸主词条识别错误", "ERROR")
                    return False
        if config.EchoSynthesisDebugMode:
            logger(f"当前声骸主词条为：{this_synthesis_echo_main_status}", "DEBUG")
        return this_synthesis_echo_main_status

    def check_echo_set():
        # 识别声骸套装属性
        region = set_region(690, 685, 1250, 945)
        text_result = wait_text_designated_area(echo.echoSetName, 2, region, 5)
        this_synthesis_echo_set = remove_non_chinese(wait_text_result_search(text_result))
        if this_synthesis_echo_set:
            if config.EchoSynthesisDebugMode:
                logger(f"当前声骸的套装为：{this_synthesis_echo_set}", "DEBUG")
            return this_synthesis_echo_set
        else:
            random_click(1000, 685)
            time.sleep(0.02)
            for i in range(18):
                control.scroll(-1, 1000 * width_ratio, 685 * height_ratio)
                time.sleep(0.02)
            time.sleep(0.8)
            random_click(1000, 685)
            text_result = wait_text_designated_area(echo.echoSetName, 2, region, 5)
            this_synthesis_echo_set = remove_non_chinese(wait_text_result_search(text_result))
            if this_synthesis_echo_set:
                if config.EchoSynthesisDebugMode:
                    logger(f"当前声骸的套装为：{this_synthesis_echo_set}", "DEBUG")
                return this_synthesis_echo_set
            else:
                logger(f"声骸套装识别错误", "ERROR")
                return False

    def check_echo_name():
        region = set_region(710, 145, 1255, 180)
        text_result = wait_text_designated_area(echo.echoName, 1, region, 3)
        this_synthesis_echo_name = remove_non_chinese(wait_text_result_search(text_result))
        if this_synthesis_echo_name:
            this_synthesis_echo_name = echo_name_check(this_synthesis_echo_name)
            if config.EchoDebugMode:
                logger(f"当前声骸名称为：{this_synthesis_echo_name}", "DEBUG")
        else:
            if config.EchoDebugMode:
                logger(f"识别声骸名称失败 (只影响显示，不影响正常判定)", "WARN")
            this_synthesis_echo_name = "未知"
        return this_synthesis_echo_name

    def lock_echo_synthesis(echo_cost, echo_main_status, echo_set, echo_name):
        log_str = (
                "" +
                f"当前是第{info.inSpecSynthesisEchoQuantity + 1}个有效声骸" +
                f"，{echo_name}" +
                f"，{echo_cost}Cost" +
                f"，{echo_set}" +
                f"，{echo_main_status}"
        )
        echo_cost = echo_cost + "COST"
        if is_echo_main_status_valid(echo_set, echo_cost, echo_main_status, config.EchoLockConfig):
            if config.EchoSynthesisDebugMode:
                logger(f"当前声骸符合要求，锁定声骸", "DEBUG")
            log_str = log_str + "，执行锁定"
            info.inSpecSynthesisEchoQuantity += 1
            control.click(1205 * width_ratio, 345 * height_ratio)
            time.sleep(0.5)
            logger(log_str)
        else:
            if config.EchoSynthesisDebugMode:
                logger(f"不符合，跳过", "DEBUG")

    def check_synthesis_echo_level_and_quantity(first_index, echo_results, click_points):
        loop_times = None
        if first_index == 0:
            loop_times = 1
        elif first_index == 1:
            loop_times = 2
        elif first_index == 3:
            loop_times = 3
        length = (len(results) + 1) // 2

        for i in range(loop_times):
            echo_index_purple = echo_results[first_index + i]
            echo_index_gold = echo_results[first_index + i + length]
            if echo_index_purple:
                logger(f"合成次数：{info.synthesisTimes}，当前已成功合成符合配置的金色声骸/已获得的金色声骸：{info.inSpecSynthesisEchoQuantity}/{info.synthesisGoldQuantity}个。")
            elif echo_index_gold:
                info.synthesisGoldQuantity += 1
                click_x, click_y = click_points[first_index + i]
                control.click(click_x * width_ratio, click_y * height_ratio)
                time.sleep(0.2)
                control.click(click_x * width_ratio, click_y * height_ratio)
                time.sleep(0.5)
                this_echo_cost = check_echo_cost()
                this_echo_main_status = check_echo_main_status(this_echo_cost)
                this_echo_set = check_echo_set()
                this_echo_name = check_echo_name()
                lock_echo_synthesis(this_echo_cost, this_echo_main_status, this_echo_set, this_echo_name)
                logger(f"合成次数：{info.synthesisTimes}，当前已成功合成符合配置的金色声骸/已获得的金色声骸：{info.inSpecSynthesisEchoQuantity}/{info.synthesisGoldQuantity}个。")
                control.esc()
                time.sleep(1.5)
            else:
                logger("声骸识别出现问题(1)", "ERROR")
        control.esc()
    if info.synthesisTimes == 0:
        logger("3秒后开始合成，请确认背包内有用声骸已锁定")
        time.sleep(3)
    synthesis_wait_time = 2.5
    if config.EchoSynthesisDebugMode:
        logger(f"等待合成中{synthesis_wait_time}", "DEBUG")
    time.sleep(synthesis_wait_time)
    info.synthesisTimes += 1
    # check_area_list = [(924, 577, 942, 596),
    #                    (856, 577, 871, 596), (995, 577, 1011, 596),
    #                    (790, 577, 804, 596), (923, 577, 942, 596), (1060, 577, 1080, 596)]
    check_point_list = [(960, 591),
                        (891, 591), (1028, 591),
                        (823, 591), (960, 591), (1096, 591)]
    click_point_list = [(960, 540),
                        (891, 540), (1028, 540),
                        (823, 540), (960, 540), (1096, 540)]
    purple = (255, 172, 255)
    gold = (255, 239, 171)
    results = []
    img = screenshot()
    for point in check_point_list:
        result = contrast_colors(point, purple, 0.85, False, img)
        results.append(result)
    purple_length = len(results)
    for point in check_point_list:
        result = contrast_colors(point, gold, 0.85, False, img)
        results.append(result)
    if results[0] or results[0 + purple_length]:
        if results[3] is False and results[3 + purple_length] is False:
            if config.EchoSynthesisDebugMode:
                true_count_purple = results[0:1].count(True)
                true_count_gold = results[0 + purple_length:1 + purple_length].count(True)
                logger(f"合成了1个声骸，其中紫色{true_count_purple}个，金色{true_count_gold}个。", "DEBUG")
            check_synthesis_echo_level_and_quantity(0, results, click_point_list)
        else:
            if config.EchoSynthesisDebugMode:
                true_count_purple = results[3:6].count(True)
                true_count_gold = results[3 + purple_length:6 + purple_length].count(True)
                logger(f"合成了3个声骸，其中紫色{true_count_purple}个，金色{true_count_gold}个。", "DEBUG")
            check_synthesis_echo_level_and_quantity(3, results, click_point_list)
    elif results[1] or results[1 + purple_length]:
        if config.EchoSynthesisDebugMode:
            true_count_purple = results[1:3].count(True)
            true_count_gold = results[1 + purple_length:3 + purple_length].count(True)
            logger(f"合成了2个声骸，其中紫色{true_count_purple}个，金色{true_count_gold}个。", "DEBUG")
        check_synthesis_echo_level_and_quantity(1, results, click_point_list)
    elif results[3] or results[3 + purple_length]:
        if config.EchoSynthesisDebugMode:
            true_count_purple = results[3:6].count(True)
            true_count_gold = results[3 + purple_length:6 + purple_length].count(True)
            logger(f"合成了3个声骸，其中紫色{true_count_purple}个，金色{true_count_gold}个。", "DEBUG")
        check_synthesis_echo_level_and_quantity(3, results, click_point_list)
    else:
        logger("声骸识别出现问题(2)", "ERROR")
        return False


def wait_text_result_search(text_result):
    result_str = str(text_result)
    match = re.search(r"text='([^']+)'", result_str)
    # logger(f"识别结果为{result_str}")
    if match:
        text_value = match.group(1)
        return text_value
    else:
        # logger("识别失败")
        return False


def is_echo_main_status_valid(this_echo_set, this_echo_cost, this_echo_main_status, echo_lock_config):
    if this_echo_set in echo_lock_config:
        if this_echo_cost in echo_lock_config[this_echo_set]:
            return this_echo_main_status in echo_lock_config[this_echo_set][this_echo_cost]
    return False


def find_pic(x_upper_left: int = None, y_upper_left: int = None,
             x_lower_right: int = None, y_lower_right: int = None,
             template_name: str = None, threshold: float = 0.8, img: np.ndarray = None,
             need_resize: bool = True, tmp_is_transparent_background: bool = False):
    if img is None:
        img = screenshot()
    region = None
    if None not in (x_upper_left, y_upper_left, x_lower_right, y_lower_right):
        region = set_region(x_upper_left, y_upper_left, x_lower_right, y_lower_right)
    template = Image.open(os.path.join(root_path, "template", template_name))
    template = np.array(template)
    result = match_template(img, template, region, threshold, need_resize, tmp_is_transparent_background)
    return result


def adapts():
    adapts_type = info.adaptsType

    def calculate_distance(w1, h1, w2, h2):
        return ((w1 - w2) ** 2 + (h1 - h2) ** 2) ** 0.5

    if adapts_type is None:
        if 1910 <= real_w <= 1930 and 1070 <= real_h <= 1090:
            logger("分辨率正确，使用原生坐标")
            info.adaptsType = 1
            info.adaptsResolution = "_1920_1080"
        elif 1270 <= real_w <= 1290 and 710 <= real_h <= 730:
            logger("分辨率正确，使用适配坐标")
            info.adaptsType = 2
            info.adaptsResolution = "_1280_720"
        else:
            logger("尝试使用相近分辨率，如有问题，请切换分辨率到 1920*1080 或者 1280*720", "WARN")
            info.adaptsType = 3
        if info.adaptsType == 3:
            distance_1920_1080 = calculate_distance(real_w, real_h, 1920, 1080)
            distance_1280_720 = calculate_distance(real_w, real_h, 1280, 720)
            if distance_1920_1080 < distance_1280_720:
                info.adaptsType = 1
                info.adaptsResolution = "_1920_1080"
            else:
                info.adaptsType = 2
                info.adaptsResolution = "_1280_720"
        info.processStartTime = datetime.now()


def remove_non_chinese(text):
    if not text:
        return False
    else:
        # 使用正则表达式匹配汉字，去除所有非汉字字符，包括括号
        result = re.sub(r'[^\u4e00-\u9fff]', '', text)
        return result


def echo_name_check(text):
    if "稚形" in text:
        text = text.replace("稚形", "")
        return f"{text}（稚形）"
    else:
        return text


def check_in_animation(img: np.ndarray = None, in_game: bool = False):
    if info.actionErrorTimes > 300:
        logger("长时间未检测到角色可行动，将重启游戏", "ERROR")
        kill_process_by_hwnd(hwnd)
    if img is None:
        img = screenshot()
    if not (
        find_pic(1720, 200, 1760, 240, f"1号角色按钮{info.adaptsResolution}.png", 0.6, img=img, need_resize=False) or
        find_pic(1720, 330, 1760, 370, f"2号角色按钮{info.adaptsResolution}.png", 0.6, img=img, need_resize=False)
    ):
        if (datetime.now() - info.lastActionErrorTime).total_seconds() > 1:
            info.actionErrorTimes += 1
            info.lastActionErrorTime = datetime.now()
        return "is animation"
    elif not find_pic(1750, 915, 1860, 1035, f"R按键{info.adaptsResolution}.png", 0.6, img=img, need_resize=False):
        # logger("当前角色无法行动", "DEBUG")
        if (datetime.now() - info.lastActionErrorTime).total_seconds() > 1:
            info.actionErrorTimes += 1
            info.lastActionErrorTime = datetime.now()
        return "character cant move"
    if in_game:
        info.inGame = True
    info.actionErrorTimes = 0
    return "is available"


def check_character_change(img: np.ndarray = None):
    character_button= {
        1: ((1720, 200, 1760, 240), f"1号角色按钮{info.adaptsResolution}.png"),
        2: ((1720, 330, 1760, 370), f"2号角色按钮{info.adaptsResolution}.png"),
        3: ((1720, 460, 1760, 510), f"3号角色按钮{info.adaptsResolution}.png"),
    }
    if img is None:
        img = screenshot()
    role_index = info.roleIndex
    role_button_coords, role_button_image = character_button[role_index]

    # 查找当前角色按钮图像
    if not find_pic(role_button_coords[0], role_button_coords[1], role_button_coords[2], role_button_coords[3], role_button_image, 0.6, img=img, need_resize=False):
        # 没有找到当前位置角色按钮的图像，表示当前角色就是info.roleIndex
        return True

    return False


def check_character_element(img: np.ndarray = None):
    element = {
        "导电": ((754, 1005), (180, 107, 255)),
        "衍射": ((747, 1003), (217, 201, 96)),
        "热熔": ((755, 998), (240, 116, 78)),
        "冷凝": ((755, 998), (64, 172, 248)),
        "气动": ((760, 997), (85, 255, 181)),
        "湮灭": ((760, 997), (200, 65, 146)),
    }
    if img is None:
        img = screenshot()
    for element_name, (coordinate, element_color) in element.items():
        if contrast_colors(coordinate, element_color, img=img, threshold=0.8):
            return element_name, element_color

    return "未知", (0, 0, 0)


def check_character_concerto_energy(
        element_color: Tuple[int, int, int],
        img: np.ndarray = None,
        threshold: float = 0.8
    ) -> str:
    if img is None:
        img = screenshot()
    energy_points = {
        "25%": (748, 980),
        "50%": (723, 1003),
        "75%": (748, 1028),
        "100%": (772, 1006)
    }
    energy_gauge = ["25%", "50%", "75%", "100%"]
    for gauge in reversed(energy_gauge):
        coord = energy_points[gauge]
        if contrast_colors(coord, element_color, threshold=threshold, img=img):
            # 确认所有低于此级别的能量点也符合
            valid = True
            for lower_level in energy_gauge[:energy_gauge.index(gauge)]:
                lower_coord = energy_points[lower_level]
                if not contrast_colors(lower_coord, element_color, threshold=0.8, img=img):
                    valid = False
                    break
            if valid:
                return gauge

    return "0%"


def check_ult():
    if check_in_animation() == "is animation":
        logger("检测到大招释放，等待大招动画", "DEBUG")
        for _ in range(12):  # 0.8秒后开始连续检测大招是否释放完毕，最大2.4秒
            if _ < 4:
                time.sleep(0.2)
            else:
                if check_in_animation() == "is animation":
                    time.sleep(0.2)
                else:
                    logger(f"大招动画结束，动画时长:{(_ + 1) * 0.2}", "DEBUG")
                    break
                if _ == 11:
                    logger(f"大招动画超时", "DEBUG")
        return True
    return False


def check_loading(leave_dungeon: bool = False, reload_search_model: bool = False):
    region = set_region(1735, 970, 1845, 1020)
    loading_progress = "0"   # 加载进度
    # loading_wait_time = 2  # 测试超时重启用
    loading_wait_time = 300   # 等待加载时间，超过则重启游戏
    loading_start_time = datetime.now()
    logger("进入加载页面，等待加载", "DEBUG")
    if reload_search_model:
        if info.echoSearchModel:
            if info.echoSearchModel == info.lastEchoSearchModel:
                logger(f"与上次模型一致，无需加载，使用模型{info.echoSearchModel}","DEBUG")
            else:
                logger(f"加载yolo模型{info.echoSearchModel}", "DEBUG")
                importlib.reload(yolo)
        else:
            info.echoSearchModel = "yolo.onnx"
            logger(f"未设置模型，使用默认yolo模型", "DEBUG")
            importlib.reload(yolo)
    i = 0
    while loading_progress != "100%" and check_in_animation() != "is available":
        text_result = wait_text_designated_area("%", 1, region, 3, full_text_return=True)
        if text_result and text_result[0].text != "":
            loading_progress = re.sub(r'\D', '', text_result[0].text)  # 只提取识别出的字符的数字部分
            logger(f"当前加载：{loading_progress}%", "DEBUG")
            if leave_dungeon:
                info.inDungeon = False
                info.lastFightTime = datetime.now()
        else:
            if i == 0:
                logger("未检测到加载进度，等待", "DEBUG")
            if i > 3:
                return False
            i += 1
            time.sleep(0.3)
        loading_time_now = datetime.now()
        if loading_time_now - loading_start_time > timedelta(seconds=loading_wait_time):
            logger(f"等待超时，重启游戏", "WARN")
            kill_process_by_hwnd(hwnd)
            return False
        time.sleep(0.2)
    logger("加载完成", "DEBUG")
    if leave_dungeon:
        info.inDungeon = False
    return True


def kill_process_by_hwnd(hwnd):
    # 获取窗口句柄对应的进程ID
    thread_id, process_id = win32process.GetWindowThreadProcessId(hwnd)
    # 使用psutil结束进程
    try:
        process = psutil.Process(process_id)
        process.terminate()  # 终止进程
        process.wait(timeout=5)  # 等待进程终止
        print(f"进程 {process_id} 已被终止。")
    except psutil.NoSuchProcess:
        print(f"进程 {process_id} 不存在。")
    except psutil.AccessDenied:
        print(f"无权限终止进程 {process_id}。")
    except psutil.TimeoutExpired:
        print(f"终止进程 {process_id} 超时。")


def check_game_restarting(del_file: bool = False):
    is_game_restarting_file = os.path.join(config.user_data_root, "isRestarting.dat")
    if del_file:
        if os.path.exists(is_game_restarting_file):
            os.remove(is_game_restarting_file)
    else:
        if os.path.exists(is_game_restarting_file):
            return True
        elif not os.path.exists(is_game_restarting_file):
            return False


def format_time(calculated_time):
    hours, remainder = divmod(calculated_time.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    formatted_all_time = f'{int(minutes):02}分钟{int(seconds):02}秒'
    return formatted_all_time


# 战斗结束后的战斗时间/吸收时间计算 以及 动态更改每个BOSS的吸收时间提高稳定性和效率
def check_fight_time(lastBossName):
    # 本次声骸搜索计数(防止一次战斗多次计数)
    info.lastAbsorptionCount = info.absorptionCount
    # 总战斗时间(包括加载和搜索声骸)
    # 治疗不需要打印
    all_time = datetime.now() - info.fightTime
    if info.needHeal:
        return False
    # 战斗次数为0时，改为显示脚本启动用时
    if info.fightCount == 0:
        formatted_all_time = format_time(all_time)
        logger(f"脚本启动用时：{formatted_all_time}", "IMPORTANT")
    elif info.fightCount == 1 and all_time.total_seconds() > 3000:
        formatted_all_time = format_time(all_time)
        logger(f"脚本重启用时：{formatted_all_time}", "IMPORTANT")
        info.fightCount = 0
    else:
        formatted_all_time = format_time(all_time)
        logger(f"本次战斗总用时：{formatted_all_time}", "IMPORTANT")
        # 仅战斗用时
        fight_time = info.fightEndTime - info.fightTime
        formatted_fight_time = format_time(fight_time)
        logger(f"战斗用时：{formatted_fight_time}", "IMPORTANT")
        # 添加本次战斗用时到当前BOSS战斗时间列表，为了防止异常数值混入，只添加<5分钟的数值
        boss_index = info.lastBossIndex % len(config.TargetBoss)
        next_boss_index = (info.lastBossIndex + 1) % len(config.TargetBoss)
        this_boss_name = config.TargetBoss[boss_index % len(config.TargetBoss)]
        next_boss_name = config.TargetBoss[(boss_index + 1) % len(config.TargetBoss)]
        logger(f"当前BOSS索引：{boss_index}，当前BOSS名称：{this_boss_name}，战斗次数：{info.bossAllFightTimes[boss_index]}，吸收次数：{info.bossAllEchoAbsorptionTimes[boss_index]}", "IMPORTANT")
        this_boss_fight_times = info.bossAllFightTime[boss_index]
        if 0 <= fight_time.total_seconds() <= 300:
            this_boss_fight_times.append(fight_time.total_seconds())
        # 计算当前BOSS的战斗平均时间(为了使其有意义，当战斗次数 > 5次以上时开始计算，保存最新的100条时间)
        try:
            if len(this_boss_fight_times) > 5:
                this_boss_average_fight_time = round(sum(this_boss_fight_times) / len(this_boss_fight_times), 2)
                logger(f"【{lastBossName}】的平均战斗时间为:{this_boss_average_fight_time}秒，已记录最近{len(this_boss_fight_times)}条战斗时间", "IMPORTANT")
        except Exception:
                pass
        # 搜索声骸用时
        if lastBossName == "无妄者" or lastBossName == "角":
            pass
        else:
            info.echoSearchEndTime = datetime.now()
        echo_search_time = info.echoSearchEndTime - info.echoSearchStartTime
        formatted_echo_search_time = format_time(echo_search_time)
        logger(f"搜索声骸用时：{formatted_echo_search_time}", "IMPORTANT")
        # 添加本次吸收用时到当前BOSS吸收时间列表，为了防止异常数值混入，只添加<60秒的吸收成功时的数值
        this_boss_echo_absorption_time = info.bossAllEchoAbsorptionTime[boss_index]
        if info.bossAllEchoAbsorptionTimes[boss_index] != info.lastBossAllEchoAbsorptionTimes[boss_index]:
            if 0 <= echo_search_time.total_seconds() <= 60:
                this_boss_echo_absorption_time.append(echo_search_time.total_seconds())
                info.lastBossAllEchoAbsorptionTimes[boss_index] = info.bossAllEchoAbsorptionTimes[boss_index]
        # 计算当前BOSS的吸收平均时间(为了使其有意义，当吸收次数 > 5次以上时开始计算，保存最新的100条时间)
        if len(this_boss_echo_absorption_time) > 5:
            this_boss_average_echo_absorption_time = round(sum(this_boss_echo_absorption_time) / len(this_boss_echo_absorption_time), 2)
            logger(f"【{lastBossName}】的平均吸收时间为:{this_boss_average_echo_absorption_time}秒，已记录最近{len(this_boss_echo_absorption_time)}条吸收时间", "IMPORTANT")
        if config.EchoAbsorptionDynamicAdjustingStrategy:
            # 更改最大空闲时间和最大吸收时间到下一个BOSS吸收平均时间 + 20% 秒，以实现动态调整每个BOSS的吸收时间，并且在下一个Boss吸收率吸收率小于50%时，使其额外增加50%(最小不能低于5秒)
            next_boss_echo_absorption_time = info.bossAllEchoAbsorptionTime[next_boss_index]
            next_boss_echo_absorption_times = info.bossAllEchoAbsorptionTimes[next_boss_index]
            next_boss_echo_absorption_time_offset = info.bossAllEchoAbsorptionTimeOffset[next_boss_index]
            # 下一个BOSS吸收次数 > 5次时开始使用动态吸收时间
            if next_boss_echo_absorption_times > 5:
                next_boss_average_echo_absorption_time = round(sum(next_boss_echo_absorption_time) / next_boss_echo_absorption_times, 2)
                # 当总吸收率小于52%时，开始动态调整最大空闲时间和最大吸收时间
                if next_boss_echo_absorption_times / info.bossAllFightTimes[next_boss_index] < 0.52:
                    if info.bossAllFightTimes[next_boss_index] - info.lastAllEchoAbsorptionTimeOffsetFightCount[next_boss_index] > 5:
                        absorption_rate_last_6_fight = (next_boss_echo_absorption_times - info.lastBossAllEchoAbsorptionTimesOffsetAbsorptionCount[next_boss_index]) / 6
                        logger(f"下一个BOSS【{next_boss_name}】的近6次吸收率为:{round(absorption_rate_last_6_fight * 100, 2)}%", "IMPORTANT")
                        # 近6次战斗吸收率小于50%，则使加算offset时间增加1秒，最大不超过5秒
                        if absorption_rate_last_6_fight < 0.5:
                            next_boss_echo_absorption_time_offset += 1 if next_boss_echo_absorption_time_offset + 1 <= 5 else 5
                            info.lastAllEchoAbsorptionTimeOffsetFlag[next_boss_index] = "Increased"
                            logger(f"下一个BOSS【{next_boss_name}】近6次吸收率低于50%，增加固定时间", "IMPORTANT")
                        else:
                            # 连续两次近6次战斗吸收率大于等于50%，则使加算offset时间减少0.5秒，最小不低于0秒
                            if info.lastAllEchoAbsorptionTimeOffsetFlag[next_boss_index] == "Unchanged":
                                next_boss_echo_absorption_time_offset -= 0.5 if next_boss_echo_absorption_time_offset - 0.5 >= 0 else 0
                                info.lastAllEchoAbsorptionTimeOffsetFlag[next_boss_index] = "Decreased"
                                logger(f"下一个BOSS【{next_boss_name}】的连续两次近6次吸收率高于50%，减少固定时间", "IMPORTANT")
                            # 如果上次调整过加算Offset时间，那么等6次战斗后再根据吸收率进行判断是否将offset时间减少
                            else:
                                info.lastAllEchoAbsorptionTimeOffsetFlag[next_boss_index] = "Unchanged"
                        info.lastAllEchoAbsorptionTimeOffsetFightCount[next_boss_index] = info.bossAllFightTimes[next_boss_index]
                        info.lastBossAllEchoAbsorptionTimesOffsetAbsorptionCount[next_boss_index] = next_boss_echo_absorption_times
                if next_boss_echo_absorption_times / info.bossAllFightTimes[next_boss_index] < 0.5:
                    if config.MaxIdleTime * 1.5 > 5:
                        config.MaxIdleTime = next_boss_average_echo_absorption_time * 1.2 * 1.5 + next_boss_echo_absorption_time_offset
                    else:
                        config.MaxIdleTime = 5 * 1.2 * 1.5 + next_boss_echo_absorption_time_offset
                    if config.MaxEchoAbsorptionTime * 1.5 > 5:
                        config.MaxEchoAbsorptionTime = next_boss_average_echo_absorption_time * 1.2 * 1.5 + next_boss_echo_absorption_time_offset
                    else:
                        config.MaxEchoAbsorptionTime = 5 * 1.2 * 1.5 + next_boss_echo_absorption_time_offset
                    logger(f"下一个BOSS【{next_boss_name}】吸收率低于50%，调整方式：平均吸收时间:{next_boss_average_echo_absorption_time}秒*1.2*1.5+固定时间:{next_boss_echo_absorption_time_offset}秒","IMPORTANT")
                else:
                    if config.MaxIdleTime * 1.5 > 5:
                        config.MaxIdleTime = next_boss_average_echo_absorption_time * 1.2 + next_boss_echo_absorption_time_offset
                    else:
                        config.MaxIdleTime = 5 * 1.2 + next_boss_echo_absorption_time_offset
                    if config.MaxEchoAbsorptionTime * 1.5 > 5:
                        config.MaxEchoAbsorptionTime = next_boss_average_echo_absorption_time * 1.2 + next_boss_echo_absorption_time_offset
                    else:
                        config.MaxEchoAbsorptionTime = 5 * 1.2 + next_boss_echo_absorption_time_offset
                    logger( f"下一个BOSS吸收率正常，调整方式：平均吸收时间:{next_boss_average_echo_absorption_time}秒*1.2+固定时间:{next_boss_echo_absorption_time_offset}秒", "IMPORTANT")
            else:
                config.MaxIdleTime = 15
                config.MaxEchoAbsorptionTime = 15
            logger(f"下一个BOSS【{next_boss_name}】的最大空闲时间和最大吸收时间已调整为：{config.MaxIdleTime}秒，{config.MaxEchoAbsorptionTime}秒","IMPORTANT")
        info.echoSearchTimesCount = 0
        info.fightEndFlagCount = 0
        info.fightEndFlag = False


def load_special_code(this_boss_name):
    config_file_path = os.path.join(config.project_root, "config.yaml")
    if not os.path.exists(config_file_path):
        return False
    with open(config_file_path, 'r', encoding='utf-8') as file:
        special_code_config_file = yaml.safe_load(file)
    if 'SpecialCode' in special_code_config_file and config.UseSpecialCode:
        special_code_boss_names = special_code_config_file['SpecialCode'].get('SpecialCodeBossName', {})
    else:
        return False
    if this_boss_name in special_code_boss_names:
        code = special_code_boss_names[this_boss_name]
        exec(code)
        return True
    else:
        return False


# 账户登录窗口专用点击方法 by wakening
def click_position_in_login_hwnd(
        position: Position,
        specified_hwnd,
        range_x: int = 3,
        range_y: int = 3,
        need_print: bool = False
):
    """
    点击位置
    :param position: 需要点击的位置
    :param specified_hwnd: 指定的窗口句柄
    :param range_x: 水平方向随机偏移的范围
    :param range_y: 垂直方向随机偏移的范围
    :param need_print: 是否输出log，debug用
    """

    def enum_child_windows_callback(child_hwnd, child_hwnds):
        child_hwnds.append(child_hwnd)

    # 分析position的中点
    x = (position.x1 + position.x2) // 2
    y = (position.y1 + position.y2) // 2
    if x is None or y is None:
        logger("没有传入坐标，无法点击", "WARN")
        return
    random_x = x + np.random.uniform(-range_x, range_x)
    random_y = y + np.random.uniform(-range_y, range_y)
    # 不需要缩放
    random_x = int(random_x)
    random_y = int(random_y)
    time.sleep(np.random.uniform(0, 0.1))  # 随机等待后点击
    # 后台发送点击消息，窗口微闪一下没反应，可能窗口过于简陋没实现该方法
    # 改成前台点击
    control.click(specified_hwnd=specified_hwnd, x=random_x, y=random_y)
    if need_print:
        logger(f"点击了父窗口坐标{random_x},{random_y}", "DEBUG")

    child_hwnds = []
    win32gui.EnumChildWindows(specified_hwnd, enum_child_windows_callback, child_hwnds)
    if child_hwnds:
        if need_print:
            logger("子窗口信息:")
        for child_hwnd in child_hwnds:
            win32gui.PostMessage(child_hwnd, win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
            control.click(specified_hwnd=child_hwnd, x=random_x, y=random_y)
            if need_print:
                logger(f"已在子窗口 '{child_hwnd}' 点击位置 ({x}, {y})","DEBUG")


# 使用传入的窗口句柄，从此窗口中获取窗口尺寸，重新绘制图像获取截图
def screenshot_in_specified_hwnd(specified_hwnd) -> np.ndarray | None:
    sp_left, sp_top, sp_right, sp_bot = win32gui.GetClientRect(specified_hwnd)
    sp_w = sp_right - sp_left
    sp_h = sp_bot - sp_top
    # logger(f"sp_w, sp_h: {sp_w}, {sp_h}")
    # 在执行方法 get_scale_factor() 前，执行 win32gui.GetClientRect()
    # 才能拿到真实的分辨率，由于此脚本引入全局变量脚本constant.py，悄悄先一步执行了
    # 所以这里调用 win32gui.GetClientRect() 拿到的是缩放后的坐标，坑啊，害我调式半天 by wakening
    # 所以这里不再乘以缩放比例
    # real_sp_w = int(sp_w * scale_factor)
    # real_sp_h = int(sp_h * scale_factor)
    real_sp_w = int(sp_w)
    real_sp_h = int(sp_h)
    hwndDC = win32gui.GetWindowDC(specified_hwnd)  # 获取窗口设备上下文（DC）
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)  # 创建MFC DC从hwndDC
    saveDC = mfcDC.CreateCompatibleDC()  # 创建与mfcDC兼容的DC
    saveBitMap = win32ui.CreateBitmap()  # 创建一个位图对象
    # logger(f"int(real_sp_w), int(real_sp_h): {int(real_sp_w)}, {int(real_sp_h)}")
    saveBitMap.CreateCompatibleBitmap(mfcDC, int(real_sp_w), int(real_sp_h))  # 创建与mfcDC兼容的位图
    saveDC.SelectObject(saveBitMap)  # 选择saveDC的位图对象，准备绘图
    # 尝试使用PrintWindow函数截取窗口图像
    result = windll.user32.PrintWindow(specified_hwnd, saveDC.GetSafeHdc(), 3)
    if result != 1:
        return None  # 如果截取失败，则返回None
    # 从位图中获取图像数据
    bmp_info = saveBitMap.GetInfo()  # 获取位图信息
    bmp_str = saveBitMap.GetBitmapBits(True)  # 获取位图数据
    im = np.frombuffer(bmp_str, dtype="uint8")  # 将位图数据转换为numpy数组
    im.shape = (bmp_info["bmHeight"], bmp_info["bmWidth"], 4)  # 设置数组形状
    im = im[:, :, [2, 1, 0, 3]][:, :, :3]  # 调整颜色通道顺序为RGB 并去掉alpha通道

    # 清理资源
    try:
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(specified_hwnd, hwndDC)
    except Exception as e:
        logger(f"清理截图资源失败: {e}", "ERROR")

    return im  # 返回截取到的图像waA


# 账户登录专用文本查找，在传入的窗口内查找文本，而非默认的全局hwnd by wakening
def find_text_in_login_hwnd(targets: str | list[str], login_hwnd) -> OcrResult | None:
    if login_hwnd is None:
        return None
    if isinstance(targets, str):
        targets = [targets]
    img = screenshot_in_specified_hwnd(login_hwnd)
    if img is None:
        return None
    result = ocr(img)
    for target in targets:
        if text_info := search_text(result, target):
            return text_info
    return None


def check_echo_is_over():
    if (info.lastEchoOverCheckTime - datetime.now()).total_seconds() > 60:
        for _ in range(3):
            logger("正在检查声骸是否已达背包上限", "DEBUG")
            region = set_region(660, 150, 1280, 290)
            if wait_text_designated_area("邮件", 2, region):
                logger("背包已满，即将前往合成", "DEBUG")
                info.lastEchoOverCheckTime = datetime.now()
                info.needSynthesis = True
                return
        logger("背包未满，继续执行Boss任务", "DEBUG")
        info.lastEchoOverCheckTime = datetime.now()


def change_task(target_task):
    import schema
    from main import start_task_change
    from task import boss_task, synthesis_task, echo_bag_lock_task
    if target_task == "合成":
        target_task = synthesis_task
        target_task_name = "合成任务"
    elif target_task == "BOSS":
        target_task = boss_task
        target_task_name = "BOSS任务"
    elif target_task == "背包声骸锁定":
        target_task = echo_bag_lock_task
        target_task_name = "背包声骸锁定任务"
    else:
        logger(f"未知的任务类型: {target_task}", "ERROR")
        return
    shared_switch_task_flag = schema.shared_switch_task_flag_run
    shared_switch_event = schema.event_run
    start_task_change(target_task, shared_switch_task_flag, shared_switch_event, schema.log_queue_run, task_name=target_task_name)


def change_task_to_synthesis():
    if info.needSynthesis:
        time.sleep(2)
        control.esc()
        time.sleep(2)
        region = set_region(0, 0, 260, 120)
        if wait_text_designated_area("终端", 2, region):
            random_click(1440, 500)
            time.sleep(2)
        else:
            logger("未找到终端，停止切换到合成任务", "DEBUG")
            info.needSynthesis = False
            return False
        if wait_text_designated_area("数据坞", 2, region):
            random_click(75, 595)
            time.sleep(2)
        else:
            logger("未找到数据坞，停止切换到合成任务", "DEBUG")
            info.needSynthesis = False
            return False
        if wait_text_designated_area("数据融合", 2, region):
            info.needSynthesis = False
            info.lastFightTime = datetime.now()
            change_task("合成")
            return True
        else:
            logger("未找到数据融合，停止切换到合成任务", "DEBUG")
            info.needSynthesis = False
            return False
    else:
        return False


def change_task_to_boss():
    for _ in range(2):
        control.esc()
        time.sleep(1)
    while check_in_animation() != "is available":
        control.esc()
        time.sleep(2)
    change_task("BOSS")


def check_synthesis_end():
    for _ in range(3):
        region = set_region(660, 150, 1280, 290)
        if wait_text_designated_area("材料不足", 2, region):
            control.activate()
            change_task_to_boss()
        return True


adapts()
