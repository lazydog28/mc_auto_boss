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
from constant import root_path, hwnd, real_w, real_h, width_ratio, height_ratio, scale_factor
from ocr import ocr
from schema import match_template, OcrResult
from control import control
from config import config
from status import info, logger
from schema import Position
from datetime import datetime
from yolo import search_echoes
from echo import echo


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
                    if config.WaitUltAnimation:  # 等待大招时间，目前4k屏，175%缩放，游戏分辨率1920*1080,测试有效，可能需要做适配
                        ult_animation_not_use = find_pic(1750, 915, 1860, 1035,f"R按键{info.adaptsResolution}.png", 0.6, need_resize=False)
                        if ult_animation_not_use is None:
                            logger("检测到大招释放，等待大招动画")
                            time.sleep(1.6)
                            release_skills_after_ult()
                            break
                else:
                    control.fight_tap(tactic)
            elif len(tactic) >= 2 and tactic[1] == "~":
                # 如果没有指定时间，默认0.5秒
                click_time = 0.5 if len(tactic) == 2 else float(tactic.split("~")[1])
                if tactic[0] == "a":
                    control.mouse_press()
                    time.sleep(click_time)
                    control.mouse_release()
                else:
                    control.key_press(tactic[0])
                    time.sleep(click_time)
                    control.key_release(tactic[0])
            elif '(' in tactic and ')' in tactic:  # 以设置的连续按键时间进行连续按键，识别格式：key(float)
                continuous_tap_time = float(tactic[tactic.find('(') + 1:tactic.find(')')])
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
            if len(tacticUlt) == 1:  # 如果只有一个字符，且为普通攻击，进行连续0.3s的点击
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
                    if config.WaitUltAnimation:  # 等待大招时间，目前4k屏，175%缩放，游戏分辨率1920*1080,测试有效，可能需要做适配
                        ult_animation_not_use = find_pic(1750, 915, 1860, 1035,f"R按键{info.adaptsResolution}.png", 0.6)
                        if ult_animation_not_use is None:
                            logger("检测到大招释放，等待大招动画")
                            time.sleep(0.5)
                            release_skills_after_ult()  # 此处或许不需要太长的等待时间，因为此处应该是二段大招(如果未来有)。
                else:
                    control.fight_tap(tacticUlt)
            elif len(tacticUlt) >= 2 and tacticUlt[1] == "~":
                # 如果没有指定时间，默认0.5秒
                click_time = 0.5 if len(tacticUlt) == 2 else float(tacticUlt.split("~")[1])
                if tacticUlt[0] == "a":
                    control.mouse_press()
                    time.sleep(click_time)
                    control.mouse_release()
                else:
                    control.key_press(tacticUlt[0])
                    time.sleep(click_time)
                    control.key_release(tacticUlt[0])
            elif '(' in tacticUlt and ')' in tacticUlt:  # 以设置的连续按键时间进行连续按键，识别格式：key(float)
                continuous_tap_time = float(tacticUlt[tacticUlt.find('(') + 1:tacticUlt.find(')')])
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
        time.sleep(3)
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
        logger("截取屏幕失败", "ERROR")
        # 释放所有资源
        try:
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
            del hwndDC, mfcDC, saveDC, saveBitMap
        except Exception as e:
            logger(f"清理截图资源失败: {e}", "ERROR")
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
        logger(f"清理截图资源失败: {e}","ERROR")
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


def wait_text_designated_area(targets: str | list[str], timeout: int = 1, region: tuple = None, max_attempts: int = 3):
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
    return_all: bool = False
) -> Union[bool, List[bool]]:
    """
    在 (x, y) 提取颜色，并与传入颜色元组进行欧氏距离对比获取相似度，并判断 。

    :param coordinates: 坐标 (x, y) 或坐标列表 [(x1, y1), (x2, y2), ...]
    :param target_colors: 目标颜色元组 (R, G, B) 或目标颜色元组列表 [(R1, G1, B1), (R2, G2, B2), ...]
    :param threshold: 相似度阈值
    :param return_all: 是否返回所有布尔值结果列表，如果为 False 则返回单个布尔值
    :return: 如果 return_all 为 True，则返回布尔值列表；否则返回单个布尔值
    """
    # 如果传入的是单个坐标和颜色，将它们转换为列表
    if isinstance(coordinates, tuple) and isinstance(target_colors, tuple):
        coordinates = [coordinates]
        target_colors = [target_colors]

    if len(coordinates) != len(target_colors):
        raise ValueError("坐标和颜色的数量必须相同")

    # 获取截图
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

        # 获取指定坐标的颜色
        color = img.getpixel(coord)

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

    def contains_any_combinations(name, keywords, min_chars):  # 为了防止BOSS名重复，添加了最小匹配关键字数
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
        logger("无妄者需要等待3秒开始战斗！", "DEBUG")
        time.sleep(3)
    else:
        logger("当前BOSS可直接开始战斗！", "DEBUG")

    info.waitBoss = False


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


def lock_echo():
    adapts()
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
            logger(f"本次总共检查{info.echoNumber}个声骸，有{info.in_spec_echo_quantity}符合条件并锁定！！\n")
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
        this_echo_main_status = wait_text_result_search(text_result)
        if config.EchoDebugMode:
            logger(f"当前声骸主词条为：{this_echo_main_status}", "DEBUG")
    else:
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
            this_echo_main_status = wait_text_result_search(text_result)
            if config.EchoDebugMode:
                logger(f"当前声骸主词条为：{this_echo_main_status}", "DEBUG")
        else:
            logger(f"声骸主词条识别错误", "ERROR")
            return False

    # 识别声骸套装属性
    region = set_region(1295, 430, 1850, 930)
    text_result = wait_text_designated_area(echo.echoSetName, 2, region, 5)
    this_echo_set = wait_text_result_search(text_result)
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
        if this_echo_set:
            if config.EchoDebugMode:
                logger(f"当前声骸为套装为：{this_echo_set}", "DEBUG")
            pass
        else:
            logger(f"声骸套装识别错误", "ERROR")
            return False

    # 声骸信息合成
    log_str = (
            "" +
            f"当前是第{info.echoNumber}个声骸" +
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
            info.in_spec_echo_quantity += 1
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
        logger(f"已划出当前边缘,滑动次数：{scroll_times_out_edge}", "DEBUG")

        scroll_times_next_edge = scroll_and_check(0, 4, "正在划到下一个边缘", lambda img: find_cost(img))
        time.sleep(0.3)

        if scroll_times_next_edge >= 4:
            logger("自动滑动至下一排超出尝试次数，使用默认值尝试", "WARN")
            return False
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
             template_name: str = None, threshold: float = 0.8, img: np.ndarray = None, need_resize: bool = True):
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
