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
import os
import win32con
import numpy as np
import itertools
from PIL import Image, ImageGrab
from ctypes import windll
from typing import List, Tuple, Union
from constant import root_path, hwnd, real_w, real_h, width_ratio, height_ratio
from ocr import ocr
from schema import match_template, OcrResult
from control import control
from config import config
from status import info, logger
from schema import Position
from datetime import datetime
from yolo import search_echoes
from echo import echo
from caculate import calculate_total_weight


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


# 账户登录窗口专用点击方法 by wakening
def click_position_in_login_hwnd(
    position: Position,
    specified_hwnd,
    range_x: int = 3,
    range_y: int = 3,
    need_print: bool = False,
):
    """
    点击位置
    :param position: 需要点击的位置
    :param specified_hwnd: 指定的窗口句柄
    :param range_x: 水平方向随机偏移的范围
    :param range_y: 垂直方向随机偏移的范围
    :param need_print: 是否输出log，debug用
    """
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
    control.click_login(random_x, random_y, specified_hwnd)
    if need_print:
        logger(f"点击了坐标{random_x},{random_y}", "DEBUG")


def select_role(reset_role: bool = False):
    now = datetime.now()
    if (now - info.lastSelectRoleTime).seconds < config.SelectRoleInterval:
        return
    info.lastSelectRoleTime = now
    if reset_role:
        info.roleIndex = 1
        info.resetRole = False
    else:
        info.roleIndex += 1
        if info.roleIndex > 3:
            info.roleIndex = 1
    control.tap(str(info.roleIndex))


def release_skills():
    adapts()
    if info.waitBoss:
        boss_wait(info.lastBossName)
    select_role(info.resetRole)
    control.mouse_middle()
    if len(config.FightTactics) < info.roleIndex:
        # config.FightTactics.append("e,q,r,a,0.1,a,0.1,a,0.1,a,0.1,a,0.1")
        config.FightTactics.append("e,q,r,a(2)")
    tactics = config.FightTactics[info.roleIndex - 1].split(",")
    for tactic in tactics:  # 遍历对应角色的战斗策略
        try:
            try:
                wait_time = float(tactic)  # 如果是数字，等待时间
                time.sleep(wait_time)
                continue
            except:
                pass
            time.sleep(np.random.uniform(0, 0.02))  # 随机等待
            if len(tactic) == 1:  # 如果只有一个字符，且为普通攻击，进行连续0.3s的点击
                if tactic == "a":
                    continuous_tap_time = 0.3
                    tap_start_time = time.time()
                    while time.time() - tap_start_time < continuous_tap_time:
                        # control.click()
                        control.fight_click()
                elif tactic == "s":
                    # control.space()
                    control.fight_space()
                elif tactic == "r":  # 大招时判断是否释放
                    control.fight_tap(tactic)
                    time.sleep(0.2)
                    if (
                        config.WaitUltAnimation
                    ):  # 等待大招时间，目前4k屏，175%缩放，游戏分辨率1920*1080,测试有效，可能需要做适配
                        ult_animation_not_use = find_pic(
                            1750,
                            915,
                            1860,
                            1035,
                            f"R按键{info.adaptsResolution}.png",
                            0.6,
                            need_resize=False,
                        )
                        if ult_animation_not_use is None:
                            logger("检测到大招释放，等待大招动画")
                            time.sleep(1.6)
                            release_skills_after_ult()
                            break
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
            elif (
                "(" in tactic and ")" in tactic
            ):  # 以设置的连续按键时间进行连续按键，识别格式：key(float)
                continuous_tap_time = float(
                    tactic[tactic.find("(") + 1 : tactic.find(")")]
                )
                try:
                    continuous_tap_time = float(continuous_tap_time)
                except ValueError:
                    pass
                tap_start_time = time.time()
                while time.time() - tap_start_time < continuous_tap_time:
                    if tactic[0] == "a":
                        control.fight_click()
                    elif tactic == "s":
                        control.fight_space()
                    else:
                        control.fight_tap(tactic)
        except Exception as e:
            logger(f"释放技能失败: {e}", "WARN")
            continue


def release_skills_after_ult():
    if len(config.FightTacticsUlt) < info.roleIndex:
        config.FightTacticsUlt.append("a(1.6),e,a(1.6),e,a(1.6),e")
    tacticsUlt = config.FightTacticsUlt[info.roleIndex - 1].split(",")
    logger(f"开始进行大招状态下的连段")
    for tacticUlt in tacticsUlt:  # 遍历对应角色的战斗策略
        try:
            try:
                wait_time = float(tacticUlt)  # 如果是数字，等待时间
                time.sleep(wait_time)
                continue
            except:
                pass
            time.sleep(np.random.uniform(0, 0.02))  # 随机等待
            if (
                len(tacticUlt) == 1
            ):  # 如果只有一个字符，且为普通攻击，进行连续0.3s的点击
                if tacticUlt == "a":
                    continuous_tap_time = 0.3
                    tap_start_time = time.time()
                    while time.time() - tap_start_time < continuous_tap_time:
                        # control.click()
                        control.fight_click()
                elif tacticUlt == "s":
                    # control.space()
                    control.fight_space()
                elif tacticUlt == "r":  # 大招时判断是否释放
                    control.fight_tap(tacticUlt)
                    time.sleep(0.2)
                    if (
                        config.WaitUltAnimation
                    ):  # 等待大招时间，目前4k屏，175%缩放，游戏分辨率1920*1080,测试有效，可能需要做适配
                        ult_animation_not_use = find_pic(
                            1750,
                            915,
                            1860,
                            1035,
                            f"R按键{info.adaptsResolution}.png",
                            0.6,
                        )
                        if ult_animation_not_use is None:
                            logger("检测到大招释放，等待大招动画")
                            time.sleep(0.5)
                            release_skills_after_ult()  # 此处或许不需要太长的等待时间，因为此处应该是二段大招(如果未来有)。
                else:
                    control.fight_tap(tacticUlt)
            elif (
                len(tacticUlt) >= 2 and tacticUlt[1] == "~"
            ):  # 如果没有指定时间，默认0.5秒
                click_time = (
                    0.5 if len(tacticUlt) == 2 else float(tacticUlt.split("~")[1])
                )
                if tacticUlt[0] == "a":
                    control.mouse_press()
                    time.sleep(click_time)
                    control.mouse_release()
                else:
                    control.key_press(tacticUlt[0])
                    time.sleep(click_time)
                    control.key_release(tacticUlt[0])
            elif (
                "(" in tacticUlt and ")" in tacticUlt
            ):  # 以设置的连续按键时间进行连续按键，识别格式：key(float)
                continuous_tap_time = float(
                    tacticUlt[tacticUlt.find("(") + 1 : tacticUlt.find(")")]
                )
                try:
                    continuous_tap_time = float(continuous_tap_time)
                except ValueError:
                    pass
                tap_start_time = time.time()
                while time.time() - tap_start_time < continuous_tap_time:
                    if tacticUlt[0] == "a":
                        control.fight_click()
                    elif tacticUlt == "s":
                        control.fight_space()
                    else:
                        control.fight_tap(tacticUlt)
        except Exception as e:
            logger(f"释放技能失败: {e}", "WARN")
            continue


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
    if not wait_text("追踪", timeout=5):
        logger("未找到追踪", "WARN")
        control.esc()
        return False
    # control.click(960 * width_ratio, 540 * height_ratio)
    random_click(960, 540)
    beacon = wait_text("借位信标", timeout=5)
    if not beacon:
        logger("未找到借位信标", "WARN")
        control.esc()
        return False
    click_position(beacon.position)
    if transfer := wait_text("快速旅行", timeout=5):
        click_position(transfer.position)
        time.sleep(0.5)
        logger("等待传送完成")
        wait_home()  # 等待回到主界面
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
        time.sleep(0.5)
        wait_home()  # 等待回到主界面
        logger("传送完成")
        time.sleep(2)
        now = datetime.now()
        info.idleTime = now  # 重置空闲时间
        info.lastFightTime = now  # 重置最近检测到战斗时间
        info.fightTime = now  # 重置战斗时间
        time.sleep(1)
        for i in range(5):
            forward()
            time.sleep(0.1)
        return True
    logger("未找到快速旅行", "WARN")
    control.esc()
    return False


def transfer() -> bool:
    if config.CharacterHeal:
        check_heal()
        if not info.needHeal:  # 检查是否需要治疗
            logger("无需治疗")
        else:
            # healBossName = "朔雷之鳞"  # 固定目标boss名称
            logger("开始治疗")
            time.sleep(1)
            info.lastBossName = "治疗"
            control.activate()
            control.tap(win32con.VK_F2)
            time.sleep(1)
            transfer_to_heal()
    bossName = config.TargetBoss[info.bossIndex % len(config.TargetBoss)]

    if info.lastBossName == "无妄者" and bossName == "无妄者":
        logger("前往无妄者 且 刚才已经前往过")
        for i in range(15):
            forward()
            time.sleep(0.1)
        now = datetime.now()
        info.idleTime = now  # 重置空闲时间
        info.lastFightTime = now  # 重置最近检测到战斗时间
        info.fightTime = now  # 重置战斗时间
        info.lastBossName = ""
        return True
    if info.lastBossName == "角" and bossName == "角":
        logger("前往角 且 刚才已经前往过")
        time.sleep(0.5)
        control.key_press(win32con.VK_LSHIFT) # 左shift向后闪避接触交互
        time.sleep(0.1)
        control.key_release(win32con.VK_LSHIFT)
        now = datetime.now()
        info.idleTime = now  # 重置空闲时间
        info.lastFightTime = now  # 重置最近检测到战斗时间
        info.fightTime = now  # 重置战斗时间
        info.lastBossName = ""
        return True
    control.activate()
    control.tap(win32con.VK_F2)
    time.sleep(1)
    if not wait_text(
        ["日志", "活跃", "挑战", "强者", "残象", "周期", "探寻", "漂泊"], timeout=7
    ):  
        logger("未进入索拉指南", "WARN")
        control.esc()
        info.lastFightTime = datetime.now()
        return False
    time.sleep(1)
    if info.needHeal:
        transfer_to_heal()
    elif bossName == "无妄者":
        info.bossIndex += 1
        return transfer_to_dreamless()
    else:
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
    saveBitMap.CreateCompatibleBitmap(
        mfcDC, int(real_sp_w), int(real_sp_h)
    )  # 创建与mfcDC兼容的位图
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


rare_chars = "鸷"


def search_text(results: List[OcrResult], target: str) -> OcrResult | None:
    target = re.sub(
        rf"[{rare_chars}]", ".", target
    )  # 判断 target 是否包含生僻字，如果包含则使用正则将生僻字替换为任意字符
    # print("\n search的target为(-2)" + str(target)) # 主词条识别失败Debug使用
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


def wait_text(targets: str | list[str], timeout: int = 5) -> OcrResult | None:
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
        # print(f"ocr是否识别成功:{text_info}") # ocr debug使用

        time.sleep(0.1)  # 每次截图和 OCR 处理之间增加一个短暂的暂停时间
    return None


def wait_home(timeout=120) -> bool:
    """
    等待回到主界面
    :param timeout:  超时时间
    :return:
    """
    start = datetime.now()
    while True:
        # 修复部分情况下导致无法退出该循环的问题。
        if (datetime.now() - start).seconds > timeout:
            close_window()
            raise Exception("等待回到主界面超时")
        img = screenshot()
        if img is None:
            time.sleep(0.3)
            continue
        results = ocr(img)
        if search_text(results, "特征码"):  # 特征码
            return True
        template = Image.open(os.path.join(root_path, r"template/背包.png"))  # 背包
        template = np.array(template)
        if match_template(img, template, threshold=0.9):
            return True
        template = Image.open(
            os.path.join(root_path, r"template/终端按钮.png")
        )  # 终端按钮
        template = np.array(template)
        if match_template(img, template, threshold=0.9):
            return True
        time.sleep(0.3)


def turn_to_search() -> int | None:
    x = None
    time.sleep(
        3
    )  # 增加延时以及搜索次数以避免boss死亡连招未结束导致前几轮次搜索不生效(ArcS17)
    for i in range(5):
        if i == 0:
            control.activate()
            control.mouse_middle()  # 重置视角
            time.sleep(1)
        img = screenshot()
        x = search_echoes(img)
        if x is not None:
            break
        if i == 4:  # 如果尝试了4次都未发现声骸，直接返回
            return
        logger("未发现声骸,转动视角")
        control.tap("a")
        time.sleep(1)
        control.mouse_middle()
        time.sleep(1)
    return x


def absorption_action():
    info.needAbsorption = False
    if config.CharacterHeal:
        info.checkHeal = True
    x = turn_to_search()
    if x is None:
        return
    start_time = datetime.now()  # 开始时间
    absorption_max_time = (
        config.MaxIdleTime / 2
        if config.MaxIdleTime / 2 > config.MaxSearchEchoesTime
        else config.MaxSearchEchoesTime
    )  # 最大吸收时间为最大空闲时间的一半与设定MaxSearchEchoesTime取较大值
    if absorption_max_time <= 10 and (info.inJue or info.inDreamless):
        absorption_max_time = 20
    last_x = None
    while (
        datetime.now() - start_time
    ).seconds < absorption_max_time:  # 未超过最大吸收时间
        img = screenshot()
        x = search_echoes(img)
        if x is None and last_x is None:
            continue
        if x is None:
            temp_x = turn_to_search()
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
            for i in range(4):
                forward()
                time.sleep(0.1)
        if absorption_and_receive_rewards({}):
            break


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
        return False
    logger("吸收声骸")
    info.absorptionCount += 1
    absorption_rate = (
        info.absorptionCount/info.fightCount 
        if info.absorptionCount/info.fightCount <= 1 
        else 1
    )
    logger(
        f"目前声骸吸收率为："
        + str(format(absorption_rate * 100, ".2f"))
        + "%",
        "DEBUG",
    )
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
    # control.click(1210 * width_ratio, 525 * height_ratio)
    random_click(1210, 525)
    if transfer := wait_text("快速旅行"):
        click_position(transfer.position)
        logger("治疗_等待传送完成")
        time.sleep(3)
        wait_home()  # 等待回到主界面
        logger("治疗_传送完成")
        now = datetime.now()
        info.idleTime = now  # 重置空闲时间
        info.lastFightTime = now  # 重置最近检测到战斗时间
        info.fightTime = now  # 重置战斗时间
        info.needHeal = False
        info.healCount += 1
        return True
    control.esc()
    return False


def check_heal():
    if info.checkHeal:
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
                time.sleep(1)
            else:
                logger(f"{info.roleIndex}号角色需要复苏")
                info.needHeal = True
                control.esc()
        info.checkHeal = False


def wait_text_designated_area(
    targets: str | list[str],
    timeout: int = 1,
    region: tuple = None,
    max_attempts: int = 3,
):
    start = datetime.now()
    if isinstance(targets, str):
        targets = [targets]

    attempt_count = 0
    while attempt_count < max_attempts:
        now = datetime.now()
        if (now - start).seconds > timeout:
            return None

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
        # print("\n ocr(img_cropped)(-1)" + str(result)) # 主词条识别失败Debug使用(-1)
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
    return_all: bool = False,
    img: np.ndarray = None,
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
    need_print: bool = False,
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


def boss_wait(bossName):
    """
    根据boss名称判断是否需要等待boss起身

    :param bossName: boss名称
    """
    bossName = bossName.lower()  # 将bossName转换为小写
    info.resetRole = True

    keywords_turtle = ["鸣", "钟", "之", "龟"]
    keywords_robot = ["聚", "械", "机", "偶"]
    keywords_dreamless = ["无", "妄", "者"]
    keywords_jue = ["角"]

    def contains_any_combinations(
        name, keywords, min_chars
    ):  # 为了防止BOSS名重复，添加了最小匹配关键字数
        for r in range(min_chars, len(keywords) + 1):
            for comb in itertools.combinations(keywords, r):
                if all(word in name for word in comb):
                    return True
        return False

    if contains_any_combinations(bossName, keywords_turtle, min_chars=2):
        logger("龟龟需要等待16秒开始战斗！", "DEBUG")
        time.sleep(16)
    elif contains_any_combinations(bossName, keywords_robot, min_chars=2):
        logger("机器人需要等待7秒开始战斗！", "DEBUG")
        time.sleep(7)
    elif contains_any_combinations(bossName, keywords_dreamless, min_chars=3):
        logger(f"无妄者需要等待{config.BossWaitTime_Dreamless}秒开始战斗！", "DEBUG")
        time.sleep(config.BossWaitTime_Dreamless)
    elif contains_any_combinations(bossName, keywords_jue, min_chars=1):
        logger(f"角需要等待{config.BossWaitTime_Jue}秒开始战斗！", "DEBUG")
        time.sleep(config.BossWaitTime_Jue)
    else:
        logger("当前BOSS可直接开始战斗！", "DEBUG")

    info.waitBoss = False


def set_region(
    x_upper_left: int = None,
    y_upper_left: int = None,
    x_lower_right: int = None,
    y_lower_right: int = None,
):
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
        y_lower_right * height_ratio,
    )
    region = tuple(map(int, region))
    return region


def echo_bag_lock():
    is_echo_ebug = False  # Debug打印开关
    adapts()
    """
    声骸锁定
    param is_echo_ebug 用于声骸识别过程Debug
    """
    # 开始执行判断
    if not config.EchoLock:
        logger("未启用该功能，请在config.yaml中更改EchoLock配置", "WARN")
        return False
    info.echoNumber += 1
    this_echo_row = info.echoNumber // 6 + 1
    this_echo_col = info.echoNumber % 6
    if this_echo_col == 0:
        this_echo_col = 6
        this_echo_row -= 1
    if info.echoNumber == 1:
        logger(
            "检测到声骸背包画面，3秒后将开始执行锁定程序，过程中请不要将鼠标移到游戏内。",
            "DEBUG",
        )
        logger(
            "tips:此功能需要关闭声骸详细描述(即在角色声骸装备处显示详情，在背包内显示简介)",
            "WARN",
        )
        logger(
            "步骤:点击键盘【C键】打开共鸣者，点击声骸，点击任意声骸，点击右上角简述将开关拨向左边",
            "WARN",
        )
        logger(
            "请使用已适配分辨率：\n  1920*1080分辨率1.0缩放\n  1600*900分辨率1.0缩放\n  1368*768分辨率1.0缩放\n  1280*720分辨率1.5缩放\n  1280*720分辨率1.0缩放",
            "WARN",
        )
        time.sleep(3)
        # 切换到时间顺序(倒序)
        logger("切换为时间倒序")
        random_click(400, 990)  # 调整点击位置以适配窗口模式下的1920*1080分辨率(ArcS17)
        time.sleep(1)
        random_click(400, 860)
        time.sleep(0.5)
        random_click(718, 23)
        time.sleep(0.5)
    if config.EchoDebugMode:
        logger(
            f"当前为第{this_echo_row}排，第{this_echo_col}个声骸 (总第{info.echoNumber}个)",
            "DEBUG",
        )
    echo_start_position = [285, 205]  # 第一个声骸的坐标
    echo_spacing = [165, 205]  # 两个声骸间的间距
    this_echo_x_position = (this_echo_col - 1) * echo_spacing[0] + echo_start_position[
        0
    ]  # 当前需要判断的声骸x坐标
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
    coordinate_unlock = find_pic(
        1700, 270, 1850, 395, f"声骸未锁定{info.adaptsResolution}.png", 0.98, img, False
    )
    # 先检测未锁定，再检测锁定，更快
    if coordinate_unlock:
        this_echo_lock = False
        info.echoIsLockQuantity = 0
        if config.EchoDebugMode:
            logger("当前声骸未锁定", "DEBUG")
    # 是否为锁定
    elif find_pic(
        1700, 270, 1850, 395, f"声骸锁定{info.adaptsResolution}.png", 0.98, img, False
    ):
        info.echoIsLockQuantity += 1
        if config.EchoDebugMode:
            logger("当前声骸已锁定", "DEBUG")
        if info.echoIsLockQuantity > config.EchoMaxContinuousLockQuantity:
            logger(
                f"连续检出已锁定声骸{info.echoIsLockQuantity}个，超出设定值，结束",
                "DEBUG",
            )
            logger(
                f"本次总共检查{info.echoNumber}个声骸，有{info.inSpecEchoQuantity}符合条件并锁定！！"
            )
            return False
        echo_next_row(info.echoNumber)
        return True
    else:
        logger("未检测到当前声骸锁定状况", "WARN")
        return False

    # 识别声骸Cost
    this_echo_cost = None
    # 先检测cost 4
    if find_pic(
        1690, 200, 1830, 240, f"COST4{info.adaptsResolution}.png", 0.98, img, False
    ):
        this_echo_cost = "4"
    elif find_pic(
        1690, 200, 1830, 240, f"COST1{info.adaptsResolution}.png", 0.98, img, False
    ):
        this_echo_cost = "1"
    elif find_pic(
        1690, 200, 1830, 240, f"COST3{info.adaptsResolution}.png", 0.98, img, False
    ):
        this_echo_cost = "3"

    if this_echo_cost is None:
        logger("未能识别到Cost", "ERROR")
        return False
    if config.EchoDebugMode:
        logger(f"当前声骸Cost为{this_echo_cost}", "DEBUG")

    this_echo_cost_key = this_echo_cost + "COST"

    # 当配置文件每个套装的这个cost值需要的词条一条也没写，即都不需要，直接跳过，不检测主词条
    this_echo_cost_not_in_echo_config = True
    for cost_config_dict in config.EchoLockConfig.values():
        this_echo_cost_not_in_echo_config &= (
            len(cost_config_dict.get(this_echo_cost_key)) == 0
        )
    if this_echo_cost_not_in_echo_config:
        if config.EchoDebugMode:
            logger(f"[Cost {this_echo_cost}]声骸都不需要，下一个", "DEBUG")
        echo_next_row(info.echoNumber)
        # 等一会，防止太快来不及挪到下一个
        time.sleep(0.3)
        return True

    # 识别声骸主词条属性
    if this_echo_cost == "4":  # 4COST描述太长，可能将副词条识别为主词条
        random_click(1510, 690)
        time.sleep(0.02)
        if (
            find_pic(
                1295,
                465,
                1360,
                515,
                f"声骸_攻击{info.adaptsResolution}.png",
                0.7,
                need_resize=False,
            )
            is None
        ):
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
    func, param = cost_mapping[this_echo_cost]
    text_result = wait_text_designated_area(func, param, region, 3)
    if is_echo_ebug:
        print(
            "\n wait_text_designated_area(0)" + str(text_result)
        )  # 主词条识别失败Debug使用
    this_echo_main_status = wait_text_result_search(text_result)
    if is_echo_ebug:
        print(
            "\n wait_text_result_search(text_result)(1)" + str(this_echo_main_status)
        )  # 主词条识别失败Debug使用
    if this_echo_main_status is False:
        # 增加对衍射伤害及湮灭伤害的识别容错
        text_result = wait_text_designated_area(
            {"灭伤害加成", "射伤害加成"}, 1, region, 3
        )
        if is_echo_ebug:
            print(
                "\n wait_text_designated_area(2)" + str(text_result)
            )  # 主词条识别失败Debug使用
        if text_result.text == "灭伤害加成":
            this_echo_main_status = "湮灭伤害加成"
        elif text_result.text == "行射伤害加成":
            this_echo_main_status = "衍射伤害加成"
        # elif text_result.text == "...":
        #     this_echo_main_status = "..."
    if is_echo_ebug:
        print(
            "\n this_echo_main_status(3)" + str(this_echo_main_status)
        )  # 主词条识别失败Debug使用
    this_echo_main_status = remove_non_chinese(this_echo_main_status)
    if config.EchoDebugMode:
        logger(f"当前声骸主词条为：{this_echo_main_status}", "DEBUG")
    if this_echo_main_status is None or this_echo_main_status is False:
        logger(f"声骸主词条识别错误", "ERROR")
        return False

    # 每个套装都不需要这个cost对应的主属性，直接跳过，不检测套装属性
    echo_main_is_not_exist_in_all_set = True
    # 每个套装都需要这个cost对应的主属性，直接锁定，不检测套装属性
    echo_main_is_exist_in_all_set = True
    for cost_config_dict in config.EchoLockConfig.values():
        echo_main_is_not_exist_in_all_set &= (
            this_echo_main_status not in cost_config_dict.get(this_echo_cost_key)
        )
        echo_main_is_exist_in_all_set &= this_echo_main_status in cost_config_dict.get(
            this_echo_cost_key
        )
    if echo_main_is_not_exist_in_all_set:
        if config.EchoDebugMode:
            logger(f"主属性[{str(this_echo_main_status)}]都不需要，下一个", "DEBUG")
        echo_next_row(info.echoNumber)
        return True
    if echo_main_is_exist_in_all_set:
        if config.EchoDebugMode:
            logger(f"主属性[{str(this_echo_main_status)}]都需要，直接锁定", "DEBUG")
        info.inSpecEchoQuantity += 1
        click_position(coordinate_unlock)
        time.sleep(0.5)
        echo_next_row(info.echoNumber)
        return True

    # 识别声骸套装属性
    region = set_region(1295, 430, 1850, 930)
    text_result = wait_text_designated_area(echo.echoSetName, 2, region, 5)
    this_echo_set = wait_text_result_search(text_result)
    this_echo_set = remove_non_chinese(this_echo_set)
    if this_echo_set:
        if config.EchoDebugMode:
            logger(f"当前声骸为套装为：{this_echo_set}", "DEBUG")
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
        this_echo_set = wait_text_result_search(text_result)
        this_echo_set = remove_non_chinese(this_echo_set)
        if this_echo_set:
            if config.EchoDebugMode:
                logger(f"当前声骸为套装为：{this_echo_set}", "DEBUG")

        # 上滚恢复到主词条页面
        random_click(1510, 690)
        time.sleep(0.02)
        for i in range(18):
            control.scroll(1, 1510 * width_ratio, 690 * height_ratio)
            time.sleep(0.02)
        time.sleep(0.8)
        random_click(1510, 690)

        if not this_echo_set:
            logger(f"声骸套装识别错误", "ERROR")
            return False

    # 声骸信息合成
    log_str = (
        ""
        + f"当前是第{info.echoNumber}个声骸"
        + f"，{this_echo_cost}Cost"
        + f"，{this_echo_set}"
        + f"，{this_echo_main_status}"
    )
    # 锁定声骸，输出声骸信息
    if is_echo_main_status_valid(
        this_echo_set, this_echo_cost_key, this_echo_main_status, config.EchoLockConfig
    ):
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
            click_position(coordinate_unlock)
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
        while local_scroll_times < min_times or (
            local_scroll_times < max_times and not check_condition(img)
        ):
            if config.EchoDebugMode:
                logger(message, "DEBUG")
            control.scroll(-1, 1120 * width_ratio, 210 * height_ratio)
            local_scroll_times += 1
            time.sleep(0.06)
            img = screenshot()
        return local_scroll_times

    def find_cost(img):
        for i in [1, 3, 4]:
            if find_pic(
                315,
                220,
                360,
                275,
                f"声骸行数滑动判断用COST{i}{info.adaptsResolution}.png",
                0.8,
                img,
                False,
            ):
                return True
        return False

    if echo_number % 6 == 0:
        random_click(1120, 210)

        scroll_times_out_edge = scroll_and_check(3, 6, "正在划出当前边缘", find_cost)
        if config.EchoDebugMode:
            logger(f"已划出当前边缘,滑动次数：{scroll_times_out_edge}", "DEBUG")

        scroll_times_next_edge = scroll_and_check(
            0, 4, "正在划到下一个边缘", lambda img: find_cost(img)
        )
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


def remove_non_chinese(text):
    if not text:
        return False
    # 使用正则表达式匹配汉字，去除所有非汉字字符，包括括号
    return re.sub(r"[^\u4e00-\u9fff]", "", text)


def echo_synthesis():
    """
    : 声骸合成锁定功能
    : update: 2024/06/26 16:16:00
    : author: RoseRin0
    """
    is_synthesis_debug = False  # Debug打印开关

    def check_echo_cost():
        this_synthesis_echo_cost = None
        cost_img = screenshot()
        if find_pic(
            1090,
            210,
            1240,
            295,
            f"合成_COST1{info.adaptsResolution}.png",
            0.98,
            cost_img,
            False,
        ):
            this_synthesis_echo_cost = "1"
        if find_pic(
            1075,
            195,
            1240,
            295,
            f"合成_COST3{info.adaptsResolution}.png",
            0.98,
            cost_img,
            False,
        ):
            this_synthesis_echo_cost = "3"
        if find_pic(
            1075,
            195,
            1240,
            295,
            f"合成_COST4{info.adaptsResolution}.png",
            0.98,
            cost_img,
            False,
        ):
            this_synthesis_echo_cost = "4"
        if this_synthesis_echo_cost is None:
            logger("未能识别到Cost", "ERROR")
            raise Exception(
                "Cost识别失败，请检查是否使用推荐分辨率：\n  1920*1080分辨率1.0缩放\n  1600*900分辨率1.0缩放\n  1368*768分辨率1.0缩放\n  1280*720分辨率1.5缩放\n  1280*720分辨率1.0缩放"
            )
            # 识别失败返回false将抛出TypeError，在此处提醒使用适配完善的分辨率(ArcS17)
        if config.EchoSynthesisDebugMode:
            logger(f"当前声骸Cost为{this_synthesis_echo_cost}", "DEBUG")
        return this_synthesis_echo_cost

    def check_echo_main_status(this_synthesis_echo_cost):
        if this_synthesis_echo_cost == "4":  # 4COST描述太长，可能将副词条识别为主词条
            random_click(1000, 685)
            time.sleep(0.02)
            if (
                find_pic(
                    715,
                    480,
                    770,
                    530,
                    f"声骸_攻击{info.adaptsResolution}.png",
                    0.7,
                    need_resize=False,
                )
                is None
            ):
                for i in range(18):
                    control.scroll(1, 1000 * width_ratio, 685 * height_ratio)
                    time.sleep(0.02)
                time.sleep(0.8)
                random_click(1000, 685)
        region = set_region(830, 440, 1250, 485)
        cost_mapping = {
            "1": (echo.echoCost1MainStatus, 1),
            "3": (echo.echoCost3MainStatus, 1),
            "4": (echo.echoCost4MainStatus, 1),
        }
        if this_synthesis_echo_cost in cost_mapping:
            func, param = cost_mapping[this_synthesis_echo_cost]
            text_result = wait_text_designated_area(func, param, region, 3)
            if is_synthesis_debug:
                print(
                    "\n wait_text_designated_area(0)" + str(text_result)
                )  # 主词条识别失败Debug使用
            this_synthesis_echo_main_status = wait_text_result_search(text_result)
            if is_synthesis_debug:
                print(
                    "\n wait_text_result_search(text_result)(1)"
                    + str(this_synthesis_echo_main_status)
                )  # 主词条识别失败Debug使用
            # 增加对衍射伤害及湮灭伤害的识别容错
            if this_synthesis_echo_main_status is False:
                text_result = wait_text_designated_area(
                    {"灭伤害加成", "射伤害加成"}, 1, region, 3
                )
                if is_synthesis_debug:
                    print(
                        "\n wait_text_designated_area(2)" + str(text_result)
                    )  # 主词条识别失败Debug使用
                if text_result.text == "灭伤害加成":
                    this_synthesis_echo_main_status = "湮灭伤害加成"
                elif text_result.text == "行射伤害加成":
                    this_synthesis_echo_main_status = "衍射伤害加成"
                if is_synthesis_debug:
                    print(
                        "\n this_echo_main_status(3)"
                        + str(this_synthesis_echo_main_status)
                    )  # 主词条识别失败Debug使用
            this_synthesis_echo_main_status = remove_non_chinese(
                this_synthesis_echo_main_status
            )
            if config.EchoSynthesisDebugMode:
                logger(f"当前声骸主词条为：{this_synthesis_echo_main_status}", "DEBUG")
            return this_synthesis_echo_main_status
        else:
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
                this_synthesis_echo_main_status = wait_text_result_search(text_result)
                if this_synthesis_echo_main_status is False:
                    text_result = wait_text_designated_area(
                        {"灭伤害加成", "射伤害加成"}, 1, region, 3
                    )
                    if text_result.text == "灭伤害加成":
                        this_synthesis_echo_main_status = "湮灭伤害加成"
                    elif text_result.text == "行射伤害加成":
                        this_synthesis_echo_main_status = "衍射伤害加成"
                this_synthesis_echo_main_status = remove_non_chinese(
                    this_synthesis_echo_main_status
                )
                if config.EchoSynthesisDebugMode:
                    logger(
                        f"当前声骸主词条为：{this_synthesis_echo_main_status}", "DEBUG"
                    )
                return this_synthesis_echo_main_status
            else:
                logger(f"声骸主词条识别错误", "ERROR")
                return False

    def check_echo_set():
        # 识别声骸套装属性
        region = set_region(690, 685, 1250, 945)
        text_result = wait_text_designated_area(echo.echoSetName, 2, region, 5)
        this_synthesis_echo_set = wait_text_result_search(text_result)
        this_synthesis_echo_set = remove_non_chinese(this_synthesis_echo_set)
        if this_synthesis_echo_set:
            if config.EchoSynthesisDebugMode:
                logger(f"当前声骸为套装为：{this_synthesis_echo_set}", "DEBUG")
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
            this_synthesis_echo_set = wait_text_result_search(text_result)
            this_synthesis_echo_set = remove_non_chinese(this_synthesis_echo_set)
            if this_synthesis_echo_set:
                if config.EchoSynthesisDebugMode:
                    logger(f"当前声骸为套装为：{this_synthesis_echo_set}", "DEBUG")
                return this_synthesis_echo_set
            else:
                logger(f"声骸套装识别错误", "ERROR")
                return False

    def lock_echo_synthesis(
        this_synthesis_echo_cost,
        this_synthesis_echo_main_status,
        this_synthesis_echo_set,
    ):
        log_str = (
            ""
            + f"当前是第{info.inSpecSynthesisEchoQuantity}个有效声骸"
            + f"，{this_synthesis_echo_cost}Cost"
            + f"，{this_synthesis_echo_set}"
            + f"，{this_synthesis_echo_main_status}"
        )
        this_synthesis_echo_cost = this_synthesis_echo_cost + "COST"
        if is_echo_main_status_valid(
            this_synthesis_echo_set,
            this_synthesis_echo_cost,
            this_synthesis_echo_main_status,
            config.EchoLockConfig,
        ):
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

    def check_synthesis_echo_level_and_quantity(
        first_index, echo_results, click_points
    ):
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
                logger(
                    f"合成次数：{info.synthesisTimes}，当前已成功合成符合配置的金色声骸/已获得的金色声骸：{info.inSpecSynthesisEchoQuantity}/{info.synthesisGoldQuantity}个。"
                )
            elif echo_index_gold:
                info.synthesisGoldQuantity += 1
                click_x, click_y = click_points[first_index + i]
                control.click(click_x * width_ratio, click_y * height_ratio)
                time.sleep(0.2)
                control.click(click_x * width_ratio, click_y * height_ratio)
                time.sleep(1.5)
                this_echo_cost = check_echo_cost()
                this_echo_main_status = check_echo_main_status(this_echo_cost)
                this_echo_set = check_echo_set()
                lock_echo_synthesis(
                    this_echo_cost, this_echo_main_status, this_echo_set
                )
                logger(
                    f"合成次数：{info.synthesisTimes}，当前已成功合成符合配置的金色声骸/已获得的金色声骸：{info.inSpecSynthesisEchoQuantity}/{info.synthesisGoldQuantity}个。"
                )
                control.esc()
                time.sleep(1.5)
            else:
                logger("声骸识别出现问题(1)", "ERROR")
        control.esc()

    adapts()
    synthesis_wait_time = 3
    if config.EchoSynthesisDebugMode:
        logger(f"等待合成中{synthesis_wait_time}", "DEBUG")
    time.sleep(synthesis_wait_time)
    info.synthesisTimes += 1
    # check_area_list = [(924, 577, 942, 596),
    #                    (856, 577, 871, 596), (995, 577, 1011, 596),
    #                    (790, 577, 804, 596), (923, 577, 942, 596), (1060, 577, 1080, 596)]
    check_point_list = [
        (960, 591),
        (891, 591),
        (1028, 591),
        (823, 591),
        (960, 591),
        (1096, 591),
    ]
    click_point_list = [
        (960, 540),
        (891, 540),
        (1028, 540),
        (823, 540),
        (960, 540),
        (1096, 540),
    ]
    purple = (255, 172, 255)
    gold = (255, 239, 171)
    results = []
    # print(results) # Debug使用
    img = screenshot()
    for point in check_point_list:
        result = contrast_colors(point, purple, 0.85, False, img)
        results.append(result)
    purple_length = len(results)
    for point in check_point_list:
        result = contrast_colors(point, gold, 0.85, False, img)
        results.append(result)
    # print(results) # Debug用(AcS17)
    if results[0] or results[0 + purple_length]:
        if results[3] is False and results[3 + purple_length] is False:
            if config.EchoSynthesisDebugMode:
                true_count_purple = results[0:1].count(True)
                true_count_gold = results[0 + purple_length : 1 + purple_length].count(
                    True
                )
                logger(
                    f"合成了1个声骸，其中紫色{true_count_purple}个，金色{true_count_gold}个。",
                    "DEBUG",
                )
            check_synthesis_echo_level_and_quantity(0, results, click_point_list)
        else:
            if config.EchoSynthesisDebugMode:
                true_count_purple = results[3:6].count(True)
                true_count_gold = results[3 + purple_length : 6 + purple_length].count(
                    True
                )
                logger(
                    f"合成了3个声骸，其中紫色{true_count_purple}个，金色{true_count_gold}个。",
                    "DEBUG",
                )
            check_synthesis_echo_level_and_quantity(3, results, click_point_list)
    elif results[1] or results[1 + purple_length]:
        if config.EchoSynthesisDebugMode:
            true_count_purple = results[1:3].count(True)
            true_count_gold = results[1 + purple_length : 3 + purple_length].count(True)
            logger(
                f"合成了2个声骸，其中紫色{true_count_purple}个，金色{true_count_gold}个。",
                "DEBUG",
            )
        check_synthesis_echo_level_and_quantity(1, results, click_point_list)
    elif results[3] or results[3 + purple_length]:
        if config.EchoSynthesisDebugMode:
            true_count_purple = results[3:6].count(True)
            true_count_gold = results[3 + purple_length : 6 + purple_length].count(True)
            logger(
                f"合成了3个声骸，其中紫色{true_count_purple}个，金色{true_count_gold}个。",
                "DEBUG",
            )
        check_synthesis_echo_level_and_quantity(3, results, click_point_list)
    else:
        logger("声骸识别出现问题(2)", "ERROR")
        logger(
            "\n合成结果识别失败，请检查是否使用推荐分辨率：\n  1920*1080分辨率1.0缩放\n  1600*900分辨率1.0缩放\n  1368*768分辨率1.0缩放\n  1280*720分辨率1.5缩放\n  1280*720分辨率1.0缩放",
            "WARN",
        )
        # 此处提醒使用适配完善的分辨率(ArcS17)
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


def is_echo_main_status_valid(
    this_echo_set, this_echo_cost, this_echo_main_status, echo_lock_config
):
    if this_echo_set in echo_lock_config:
        if this_echo_cost in echo_lock_config[this_echo_set]:
            return (
                this_echo_main_status in echo_lock_config[this_echo_set][this_echo_cost]
            )
    return False


def find_pic(
    x_upper_left: int = None,
    y_upper_left: int = None,
    x_lower_right: int = None,
    y_lower_right: int = None,
    template_name: str = None,
    threshold: float = 0.8,
    img: np.ndarray = None,
    need_resize: bool = True,
):
    if img is None:
        img = screenshot()
    region = None
    if None not in (x_upper_left, y_upper_left, x_lower_right, y_lower_right):
        region = set_region(x_upper_left, y_upper_left, x_lower_right, y_lower_right)
    template = Image.open(os.path.join(root_path, "template", template_name))
    template = np.array(template)
    result = match_template(img, template, region, threshold, need_resize)
    return result


def adapts():
    adapts_type = info.adaptsType

    def calculate_distance(w1, h1, w2, h2):
        return ((w1 - w2) ** 2 + (h1 - h2) ** 2) ** 0.5

    if adapts_type is None:
        if 1910 <= real_w <= 1930 and 1070 <= real_h <= 1090:  # 判断适配1920*1080
            logger("分辨率正确，使用原生坐标")
            info.adaptsType = 1
            info.adaptsResolution = "_1920_1080"
        elif 1590 <= real_w <= 1610 and 890 <= real_h <= 910:  # 判断适配1600*900
            logger("分辨率正确，使用适配坐标")
            info.adaptsType = 2
            info.adaptsResolution = "_1600_900"
        # elif 1430 <= real_w <= 1450 and 890 <= real_h <= 910: # template比例实际与1600*900相同但region需要重设(ArcS17)
        #     logger("分辨率正确，使用通用坐标")
        #     info.adaptsType = 2
        #     info.adaptsResolution = "_1600_900"
        elif 1360 <= real_w <= 1380 and 750 <= real_h <= 790:  # 判断适配1366*768
            logger("分辨率正确，使用适配坐标")
            info.adaptsType = 3
            info.adaptsResolution = "_1366_768"
        elif 1270 <= real_w <= 1290 and 710 <= real_h <= 730:  # 判断适配1280*720
            logger("分辨率正确，使用适配坐标")
            info.adaptsType = 4
            info.adaptsResolution = "_1280_720"
        else:
            logger(
                "尝试使用相近分辨率，如有问题，请切换分辨率到 1920*1080*1.0 或者 1280*720*1.0",
                "WARN",
            )
            info.adaptsType = 5
        if info.adaptsType == 5:
            distance_1920_1080 = calculate_distance(real_w, real_h, 1920, 1080)
            distance_1600_900 = calculate_distance(real_w, real_h, 1600, 900)
            distance_1366_768 = calculate_distance(real_w, real_h, 1366, 768)
            distance_1280_720 = calculate_distance(real_w, real_h, 1280, 720)
            if distance_1920_1080 < distance_1600_900:
                info.adaptsType = 1
                info.adaptsResolution = "_1920_1080"
            elif distance_1600_900 < distance_1366_768:
                info.adaptsType = 2
                info.adaptsResolution = "_1600_900"
            elif distance_1366_768 < distance_1280_720:
                info.adaptsType = 3
                info.adaptsResolution = "_1366_768"
            else:
                info.adaptsType = 4
                info.adaptsResolution = "_1280_720"


# 监测游戏是否卡加载，长时间卡在加载界面就干掉游戏进程
def anti_stuck_monitor(img, anti_stuck_list: list, last_timestamp: int) -> int | None:
    now_timestamp = int(time.time())
    # 隔一段时间(秒)收集一次
    if now_timestamp - last_timestamp < 20:
        return None
    if img is None:
        anti_stuck_list.clear()
        return None
    height, width, channels = img.shape
    # 裁右下角，避开UID
    region = (
        int(width * 0.89),
        int(height * 0.87),
        int(width * 0.98),
        int(height * 0.96),
    )
    img_pil = Image.fromarray(img).crop(region)
    stuck_img = np.array(img_pil)
    result = ocr(stuck_img)
    text_ocr_result = None
    if result is not None and len(result) > 0:
        text_ocr_result = search_text(result, "^\\d{1,3}\\s*%$")
    # 需要一段时间内连续检出正在加载中，且加载值不变，才断定为卡加载
    # 所以检查到有非加载中状态，说明这段时间没有卡死，就清空检查队列
    if text_ocr_result is None:
        anti_stuck_list.clear()
        return now_timestamp
    percent_str = text_ocr_result.text.replace(" ", "").replace("%", "")
    anti_stuck_list.append((now_timestamp, int(percent_str)))
    # 没攒够先不检测
    if len(anti_stuck_list) < 9:
        return now_timestamp
    recent_timestamp = 0
    last_timestamp = 0
    last_percent = 0
    is_stuck = True
    for i in range(len(anti_stuck_list)):
        timestamp, percent = anti_stuck_list[i]
        if i > 0:
            recent_timestamp = timestamp
            is_stuck &= last_percent == percent
        elif i == 0:
            last_timestamp = timestamp
            last_percent = percent
    anti_stuck_list.clear()
    # 加载进度有不同值，说明没卡死
    if not is_stuck:
        return now_timestamp
    logger(
        f"监测到游戏在{recent_timestamp - last_timestamp}s内连续卡在进度{last_percent}%, 关闭游戏",
        "WARN",
    )
    win32gui.SendMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    return now_timestamp


# 关闭窗口
def close_window(class_name: str = "UnrealWindow", window_title: str = "鸣潮  "):
    # 尝试关闭窗口，如果成功返回 True，否则返回 False
    hwnd = win32gui.FindWindow(class_name, window_title)
    if hwnd != 0:
        win32gui.SendMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        # 等待窗口关闭
        time.sleep(2)
        if win32gui.FindWindow(class_name, window_title) == 0:
            return True
    return False

# 声骇得分计算
def role_equip_points():

    if not config.EnhancedComputing:
        logger("未启用该功能，请在config.yaml中更改EnhancedComputing配置", "WARN")
        return False

    logger("默认按正常比例适配计算，如需计算特殊角色，请前往配置文件中配置", "WARN")
    logger("计算需要在角色声骇详情页面进行，请确保前往顺序为 按下C -> 属性详情 -> 声骇 -> 点击右侧声骇 即可。请确保处于该页面，否则可能识别失败。","WARN")
    time.sleep(1)

    logger("目前支持特殊计算角色：\n - 今汐\n - 忌炎  ")
    role_name = config.ComputeRoleName
    max_attempts = 10
    retry_interval = 5

    logger("共进行{}次尝试，每隔{}秒进行一次识别，请在一次识别后手动选择另一个声骇".format(max_attempts, retry_interval), "DEBUG")
    grade  = 0
    compute_static = config.ComputeTactic
    if len(compute_static) < 4:
        logger("声骇计算配置错误，请检查配置文件", "ERROR")

    for attempt in range(max_attempts):
        img = screenshot()
        if img is None:
            time.sleep(0.2)
            continue

        img_entry = img[205:320, 965:1220]
        img_pil2 = img[100:160, 930:1000]

        result = ocr(img_pil2)

        up = 0
        for item in result:
            if "+" in item.text:
                try:
                    up = int(item.text.split("+")[1])
                except ValueError:
                    up = -1
                break
            else:
                up = -1
        if up == -1:
            logger("声骸等级识别失败，请检查识别内容", "WARN")
            print(f"{result}")
            return False

        result = ocr(img_entry)

        if not result and up > 5 :
            for _ in range(3):
                logger("声骸识别失败，尝试重新识别", "WARN")
                result = ocr(img_entry)
                if result:
                    break

            if not result:
                print(f"{result}")
                print(f"{up}")
                logger(f"声骸识别失败，请检查识别内容{up},{result}", "WARN")
                return False
        if up < 10:
            result = result[:2]
            grade = 0
        elif up < 15:
            result = result[:4]
            grade = 1
        elif up < 20:
            result = result[:6]
            grade = 2
        elif up < 25:
            result = result[:8]
            grade = 3
        elif up == 25:
            result = result[:10]
            grade = -1

        paired_results = []
        for i in range(0, len(result), 2):
            if i + 1 < len(result):
                if "骸" in result[i].text:
                    break  # 检测到“骸”字，结束循环
                if "攻击" in result[i].text and "%" in result[i+1].text:
                    paired_results.append(("大" + result[i].text, result[i+1].text))
                else:
                    paired_results.append((result[i].text, result[i+1].text))
        if not paired_results and up < 5:
            logger("当前声骸等级{up}，声骇等级过低，无法计算，请重新选择", "WARN")
            time.sleep(retry_interval)
            continue

        print("\n---------------------------------------------------------- \n")
        total_weight, adjusted_total_weight, max_total_weight, max_adjusted_total_weight  = calculate_total_weight(paired_results, role_name)
        print(f"当前计分模型中，伤害型角色通用最高分为228.2,特殊伤害加成提升最高分为251.4,可自行参考比对")
        if adjusted_total_weight is not None:
            print(f"当前声骸等级{up},角色{role_name}本套声骇上限最高分为：{max_adjusted_total_weight}，角色{role_name}计算得分为：{adjusted_total_weight}")
        else:
            print(f"当前声骸等级{up},本套声骇上限最高分为：{max_total_weight}，计算得分为：{total_weight}")
        if grade != -1:
            if role_name == "默认" or adjusted_total_weight is None:
                print(f"当前声骇等级{up}，计算得分为：{total_weight}, 期望分为：{compute_static[grade]}，请自行确认比较")
            else :
                print(f"当前声骇等级{up}，计算得分为：{max_adjusted_total_weight}, 期望分为：{compute_static[grade]}，请自行确认比较")
        print("\n----------------------------------------------------------- \n")
        time.sleep(retry_interval)

    return False