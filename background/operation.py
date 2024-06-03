# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: operation.py
@time: 2024/5/26 下午9:17
@author SuperLazyDog
"""
import time
import numpy as np
from utils import (
    screenshot,
    matchTemplate,
    search_text,
    ocr,
    hwnd,
    width_ratio,
    height_ratio,
    root_path,
    wait_text,
    find_text,
    logger_msg,
)
from PIL import Image
from control import Control
import os
from config import config, role
import win32con
from datetime import datetime

select_role_index = 1
control = Control(hwnd)


def interactive():
    control.tap("f")


last_select_role_time = time.time()


def click_position(position: list[list[int]]):
    """
    [[       1135,         282],
       [       1445,         282],
       [       1445,         306],
       [       1135,         306]]
    :param position:
    :return:
    """
    # 分析position的中点
    x = 0
    y = 0
    for i in range(4):
        x += position[i][0]
        y += position[i][1]
    x = x // 4
    y = y // 4
    control.click(x, y)


def select_role():
    global last_select_role_time, select_role_index
    if time.time() - last_select_role_time < config.SelectRoleInterval:
        return
    last_select_role_time = time.time()
    select_role_index += 1
    if select_role_index > 3:
        select_role_index = 1
    control.tap(str(select_role_index))


def release_skills():
    select_role()
    control.mouse_middle()
    if len(config.FightTactics) < select_role_index:
        config.FightTactics.append("e,q,r,a,0.1,a,0.1,a,0.1,a,0.1,a,0.1")
    tactics = config.FightTactics[select_role_index - 1].split(",")
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
            logger_msg(f"释放技能失败: {e}")
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


def transfer_beacon() -> bool:
    """
    传送信标
    :return:
    """
    control.activate()
    control.tap("m")
    time.sleep(1)
    for i in range(20):
        control.click(1810 * width_ratio, 315 * height_ratio)
    img = screenshot()
    template = Image.open(os.path.join(root_path, r"template\借位信标.png"))
    template = np.array(template)
    coordinate = matchTemplate(img, template)
    if not coordinate:
        control.esc()
        return False
    control.click(coordinate.get("x"), coordinate.get("y"))
    time.sleep(1)
    img = screenshot()
    result = ocr(img)
    text_info = search_text(result, "借位信标")
    if not text_info:
        control.esc()
        return False
    click_position(text_info.get("position"))
    time.sleep(1)
    control.click(1745 * width_ratio, 1000 * height_ratio)
    return True


def mouse_scroll():
    control.scroll(1)
    time.sleep(1)


def select_levels():
    interactive()
    result = wait_text("推荐等级40")
    if not result:
        control.esc()
        return
    for i in range(3):
        click_position(result.get("position"))
        time.sleep(1)
    result = find_text("单人挑战")
    if not result:
        control.esc()
        return
    click_position(result.get("position"))
    time.sleep(1)


def transfer_boss() -> bool:
    control.activate()
    control.tap(win32con.VK_F2)
    if not wait_text(["日志", "活跃度", "周期挑战", "强者之路", "残象"]):
        logger_msg("未进入索拉指南")
        control.esc()
        return False
    time.sleep(1)
    img = screenshot()
    template = Image.open(os.path.join(root_path, r"template/残象探寻.png"))
    template = np.array(template)
    coordinate = matchTemplate(img, template, threshold=0.5)
    if not coordinate:
        logger_msg("识别残像探寻失败")
        control.esc()
        return False
    control.click(coordinate.get("x"), coordinate.get("y"))  # 进入残像探寻
    if not wait_text("探测"):
        logger_msg("未进入残像探寻")
        control.esc()
        return False
    bossName = config.TargetBoss[role.bossIndex % len(config.TargetBoss)]
    logger_msg(f"当前目标boss：{bossName}")
    role.bossIndex += 1
    findBoss = None
    for i in range(20):
        findBoss = find_text(bossName)
        if findBoss:
            break
        control.scroll(-20, 500 * width_ratio, 500 * height_ratio)
        time.sleep(0.3)
    if not findBoss:
        control.esc()
        logger_msg("未找到目标boss")
        return False
    click_position(findBoss.get("position"))
    click_position(findBoss.get("position"))
    time.sleep(1)
    control.click(1700 * width_ratio, 980 * height_ratio)
    if not wait_text("追踪"):
        control.esc()
        return False
    control.click(960 * width_ratio, 540 * height_ratio)
    beacon = wait_text("借位信标")
    if not beacon:
        control.esc()
        return False
    click_position(beacon.get("position"))
    if transfer := wait_text("快速旅行"):
        click_position(transfer.get("position"))
        logger_msg("等待传送完成")
        wait_text("特征码", 99999)
        role.idleTime = datetime.now()  # 重置空闲时间
        role.lastFightTime = datetime.now()  # 重置最近检测到战斗时间
        role.fightTime = datetime.now()  # 重置战斗时间
        return True
    control.esc()
    return False
