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
import numpy as np
from PIL import Image

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
    # control.click(x, y)
    random_click(x, y, ratio = False)   #找图所得坐标不需要缩放！
    


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
            time.sleep(np.random.uniform(0, 0.05))  # 随机等待
            if len(tactic) == 1:  # 如果只有一个字符，点击
                if tactic == "a":
                    control.click()
                elif tactic == "s":
                    control.space()
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
        # control.click(855 * width_ratio, y * height_ratio)
        random_click(855, y, 1, 3)
        time.sleep(0.3)
    if not findBoss:
        control.esc()
        logger("未找到目标boss")
        return False
    click_position(findBoss.position)
    click_position(findBoss.position)
    time.sleep(1)
    # control.click(1700 * width_ratio, 980 * height_ratio)
    random_click(1700, 980)
    if not wait_text("追踪"):
        logger("未找到追踪")
        control.esc()
        return False
    # control.click(960 * width_ratio, 540 * height_ratio)
    random_click(960, 540)
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
        info.lastBossName = bossName
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
    time.sleep(2)
    findBoss = find_text("战歌")
    if not findBoss:
        control.esc()
        logger("未找到战歌重奏")
        return False
    click_position(findBoss.position)
    click_position(findBoss.position)
    time.sleep(1)
    random_click(1720, 420)
    # control.click(1720 * width_ratio, 420 * height_ratio)
    if transfer := wait_text("快速旅行"):
        click_position(transfer.position)
        logger("等待传送完成")
        time.sleep(3)
        wait_home()  # 等待回到主界面
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
    logger("未找到快速旅行")
    control.esc()
    return False


def transfer() -> bool:
    if config.CharacterHeal:
        check_heal()
        if not info.needHeal:  # 检查是否需要治疗
            logger("无需治疗")
        else:
            healBossName = "朔雷之鳞"  # 固定目标boss名称
            logger("开始治疗")
            time.sleep(1)
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
    control.activate()
    control.tap(win32con.VK_F2)
    if not wait_text(
            ["日志", "活跃", "挑战", "强者", "残象", "周期", "探寻", "漂泊"], timeout=5
    ):
        logger("未进入索拉指南")
        control.esc()
        info.lastFightTime = datetime.now()
        return False
    time.sleep(1)
    if info.needHeal:
        transfer_to_heal(healBossName)
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
        logger("截取屏幕失败")
        # 释放所有资源
        try:
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
            del hwndDC, mfcDC, saveDC, saveBitMap
        except Exception as e:
            logger(f"清理截图资源失败: {e}")
        return screenshot()  # 如果截取失败，则重试

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
        logger(f"清理截图资源失败: {e}")
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
        #修复部分情况下导致无法退出该循环的问题。
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


def turn_to_search() -> int | None:
    x = None
    for i in range(4):
        if i == 0:
            control.activate()
            control.mouse_middle()  # 重置视角
            time.sleep(1)
        img = screenshot()
        x = search_echoes(img)
        if x is not None:
            break
        if i == 3:  # 如果尝试了4次都未发现声骸，直接返回
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
        config.MaxIdleTime / 2 if config.MaxIdleTime / 2 > 10 else 10
    )  # 最大吸收时间为最大空闲时间的一半或者10秒-取最大值
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
            control.tap("w")
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
    return True

def transfer_to_heal(healBossName):
    """
    如果需要治疗，传送到固定位置进行治疗。
    """
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
        logger("治疗_未找到神像附近点位BOSS(朔雷之鳞)")
        return False
    click_position(findBoss.position)
    click_position(findBoss.position)
    time.sleep(1)
    # control.click(1700 * width_ratio, 980 * height_ratio)
    random_click(1700, 980)
    if not wait_text("追踪"):
        logger("治疗_未找到追踪")
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
            region = (325 * width_ratio, 190 * height_ratio, 690 * width_ratio, 330 * height_ratio)
            region = tuple(map(int, region))
            if not wait_text_heal("复苏", timeout=3, region=region):
                logger(f"{info.roleIndex}号角色无需复苏")
                info.needHeal = False
                time.sleep(1)
            else:
                logger(f"{info.roleIndex}号角色需要复苏")
                info.needHeal = True
                control.esc()
        info.checkHeal = False

def wait_text_heal(targets: str | list[str], timeout: int = 1, region: tuple = None, max_attempts: int = 3):
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
        #print(f"Original image size: {img.shape}")

        # 将NumPy数组转换为Pillow图像对象
        img_pil = Image.fromarray(img)

        # 如果提供了具体的坐标区域，则裁剪图像
        if region:
            # 将坐标区域转换为整数
            region = tuple(map(int, region))
            # 调试输出裁剪区域
            #print(f"Cropping region: {region}")
            img_pil = img_pil.crop(region)

        # 将裁剪后的 Pillow 图像对象转换回 NumPy 数组
        img_cropped = np.array(img_pil)

        result = ocr(img_cropped)
        for target in targets:
            if text_info := search_text(result, target):
                return text_info

        attempt_count += 1
        time.sleep(0.1)  # 每次截图和 OCR 处理之间增加一个短暂的暂停时间

    return None

def random_click(x: int = None, y: int = None, range_x: int = 3, range_y: int = 3, ratio: bool = True):
    """
    在以 (x, y) 为中心的区域内随机选择一个点并模拟点击。
    
    :param x: 中心点的 x 坐标
    :param y: 中心点的 y 坐标
    :param range_x: 水平方向随机偏移的范围
    :param range_y: 垂直方向随机偏移的范围
    """
    if x is None or y is None:
        logger("没有传入坐标，无法点击")
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
        # logger(f"点击了坐标{random_x},{random_y}")