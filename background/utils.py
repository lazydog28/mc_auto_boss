# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: operation.py
@time: 2024/5/26 下午9:17
@author SuperLazyDog
"""
import re
import time
from ctypes import windll
from typing import List

import numpy as np
import win32gui
import win32ui
from constant import root_path, hwnd, real_w, real_h, width_ratio, height_ratio
from ocr import ocr
from schema import match_template, OcrResult
from control import control
import os
from config import config
from status import info, logger
from schema import Position
import win32con
from datetime import datetime

from yolo import search_echoes


def interactive():
    control.tap("f")


def click_position(position: Position):
    """
    点击位置
    """
    # 分析position的中点
    x = (position.x1 + position.x2) // 2
    y = (position.y1 + position.y2) // 2
    control.click(x, y)


def select_role():
    now = datetime.now()
    if (now - info.lastSelectRoleTime).seconds < config.SelectRoleInterval:
        return
    info.lastSelectRoleTime = now
    info.roleIndex += 1
    if info.roleIndex > 3:
        info.roleIndex = 1
    control.tap(str(info.roleIndex))


def release_skills():
    select_role()
    control.mouse_middle()
    if len(config.FightTactics) < info.roleIndex:
        config.FightTactics.append("e,q,r,a,0.1,a,0.1,a,0.1,a,0.1,a,0.1")
    tactics = config.FightTactics[info.roleIndex - 1].split(",")
    for tactic in tactics:  # 遍历对应角色的战斗策略
        try:
            try:
                wait_time = float(tactic)  # 如果是数字，等待时间
                time.sleep(wait_time)
                continue
            except:
                pass
            if len(tactic) == 1:  # 如果只有一个字符，点击
                if tactic == "a":
                    control.click()
                else:
                    control.tap(tactic)
            if len(tactic) == 2 and tactic[1] == "~":  # 如果没有指定时间，默认0.5秒
                tactic = tactic + "0.5"
            if len(tactic) >= 3 and tactic[1] == "~":
                click_time = float(tactic.split("~")[1])
                if tactic[0] == "a":
                    control.mouse_press()
                    time.sleep(click_time)
                    control.mouse_release()
                else:
                    control.key_press(tactic[0])
                    time.sleep(click_time)
                    control.key_release(tactic[0])
        except Exception as e:
            logger(f"释放技能失败: {e}")
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
    img = screenshot()
    template = Image.open(os.path.join(root_path, r"template/残象探寻.png"))
    template = np.array(template)
    coordinate = match_template(img, template, threshold=0.5)
    if not coordinate:
        logger("识别残像探寻失败")
        control.esc()
        return False
    click_position(coordinate)  # 进入残像探寻
    if not wait_text("探测"):
        logger("未进入残象探寻")
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
        control.click(855 * width_ratio, y * height_ratio)
        time.sleep(0.3)
    if not findBoss:
        control.esc()
        logger("未找到目标boss")
        return False
    click_position(findBoss.position)
    click_position(findBoss.position)
    time.sleep(1)
    control.click(1700 * width_ratio, 980 * height_ratio)
    if not wait_text("追踪"):
        logger("未找到追踪")
        control.esc()
        return False
    control.click(960 * width_ratio, 540 * height_ratio)
    beacon = wait_text("借位信标")
    if not beacon:
        logger("未找到借位信标")
        control.esc()
        return False
    click_position(beacon.position)
    if transfer := wait_text("快速旅行"):
        click_position(transfer.position)
        logger("等待传送完成")
        time.sleep(3)
        wait_home()  # 等待回到主界面
        logger("传送完成")
        now = datetime.now()
        info.idleTime = now  # 重置空闲时间
        info.lastFightTime = now  # 重置最近检测到战斗时间
        info.fightTime = now  # 重置战斗时间
        return True
    control.esc()
    return False


def transfer_to_dreamless():
    img = screenshot()
    template = Image.open(os.path.join(root_path, r"template/周期挑战.png"))
    template = np.array(template)
    coordinate = match_template(img, template, threshold=0.5)
    if not coordinate:
        logger("识别周期挑战失败")
        control.esc()
        return False
    click_position(coordinate)  # 进入周期挑战
    if not wait_text("前往"):
        logger("未进入周期挑战")
        control.esc()
        return False
    logger(f"当前目标boss：无妄者")
    findBoss = find_text("战歌")
    click_position(findBoss.position)
    click_position(findBoss.position)
    time.sleep(1)
    control.click(1720 * width_ratio, 420 * height_ratio)
    if transfer := wait_text("快速旅行"):
        click_position(transfer.position)
        logger("等待传送完成")
        time.sleep(3)
        wait_home()  # 等待回到主界面
        now = datetime.now()
        info.idleTime = now  # 重置空闲时间
        info.lastFightTime = now  # 重置最近检测到战斗时间
        info.fightTime = now  # 重置战斗时间
        for i in range(5):
            forward()
        return True
    logger("未找到快速旅行")
    control.esc()
    return False


def transfer() -> bool:
    control.activate()
    control.tap(win32con.VK_F2)
    if not wait_text(["日志", "活跃度", "周期挑战", "强者之路", "残象"], timeout=5):
        logger("未进入索拉指南")
        control.esc()
        info.lastFightTime = datetime.now()
        return False
    time.sleep(1)
    bossName = config.TargetBoss[info.bossIndex % len(config.TargetBoss)]
    info.bossIndex += 1
    if bossName == "无妄者":
        return transfer_to_dreamless()
    else:
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
        logger("截取屏幕失败")
        return screenshot()  # 如果截取失败，则重试

    # 从位图中获取图像数据
    bmp_info = saveBitMap.GetInfo()  # 获取位图信息
    bmp_str = saveBitMap.GetBitmapBits(True)  # 获取位图数据
    im = np.frombuffer(bmp_str, dtype="uint8")  # 将位图数据转换为numpy数组
    im.shape = (bmp_info["bmHeight"], bmp_info["bmWidth"], 4)  # 设置数组形状
    # 调整通道顺序 并 去除alpha通道
    im = im[:, :, [2, 1, 0, 3]][:, :, :3]

    # 清理资源
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

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


from PIL import Image


def wait_text(targets: str | list[str], timeout: int = 3) -> OcrResult | None:
    start = datetime.now()
    if isinstance(targets, str):
        targets = [targets]
    while True:
        img = screenshot()
        if img is None:
            continue
        if (datetime.now() - start).seconds > timeout:
            return None
        result = ocr(img)
        for target in targets:
            if text_info := search_text(result, target):
                return text_info
    return None


def wait_home(timeout=120):
    """
    等待回到主界面
    :param timeout:  超时时间
    :return:
    """
    start = datetime.now()
    while True:
        img = screenshot()
        if img is None:
            continue
        if (datetime.now() - start).seconds > timeout:
            return None
        results = ocr(img)
        if text_info := search_text(results, "特征码"):  # 特征码
            return text_info
        template = Image.open(os.path.join(root_path, r"template/背包.png"))  # 背包
        template = np.array(template)
        if match_template(img, template, threshold=0.9):
            return
        template = Image.open(os.path.join(root_path, r"template/终端按钮.png"))  # 终端按钮
        template = np.array(template)
        if match_template(img, template, threshold=0.9):
            return


def absorption_action():
    start_time = datetime.now()  # 开始时间
    absorption_max_time = (
        config.MaxIdleTime / 2 if config.MaxIdleTime / 2 > 10 else 10
    )  # 最大吸收时间为最大空闲时间的一半或者10秒
    while (
            datetime.now() - start_time
    ).seconds < absorption_max_time:  # 未超过最大吸收时间
        x = None
        for i in range(4):
            img = screenshot()
            x = search_echoes(img)
            if x is not None:
                break
            logger("未发现声骸,转动视角")
            control.tap("a")
            time.sleep(1)
            control.mouse_middle()
            time.sleep(1)
        if x is None:
            continue
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
        if find_text("吸收"):
            logger("吸收")
            interactive()
            time.sleep(1)
            info.absorptionCount += 1
            break
    info.needAbsorption = False
