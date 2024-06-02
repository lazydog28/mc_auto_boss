from utils import screenshot, ocr, search_text
import time
from pynput.keyboard import Listener, Key
from threading import Thread
from utils import logger_msg, width_ratio, height_ratio
from operation import (
    interactive,
    release_skills,
    click_position,
    mouse_scroll,
    transfer_boss,
    control,
    forward,
    leaving_battle,
    select_levels
)
from config import config, role, Status
from datetime import datetime
from mouse_reset import mouse_reset_event

running = False

logger_msg("初始化完成")


def boss_task():
    img = screenshot()
    ocrResults = ocr(img)
    if search_text(ocrResults, "吸收"):
        logger_msg("吸收")
        mouse_scroll()
        interactive()
        time.sleep(1)
        return
    now = datetime.now()
    for result in ocrResults:
        if "击败" in result.get("text"):
            logger_msg("战斗中")
            release_skills()
            if role.status == Status.idle:
                role.fightTime = now
            role.status = Status.fight
            role.lastFightTime = now
        if "取消" in result.get("text"):
            logger_msg("取消")
            click_position(result.get("position"))
            break
        if "终端" in result.get("text"):
            logger_msg("终端")
            control.esc()
            time.sleep(1)
    if (now - role.lastFightTime).seconds > config.MaxIdleTime:  # 检查是否长时间没有检测到战斗状态
        role.status = Status.idle
        logger_msg("长时间没有检测到战斗状态")
        role.idleTime = now  # 重置空闲时间
        role.lastFightTime = now  # 重置最近检测到战斗时间
        transfer_boss()
    if (now - role.fightTime).seconds > config.MaxFightTime:  # 长时间处于战斗状态
        logger_msg("长时间处于战斗状态 传送")
        role.idleTime = now
        role.fightTime = now  # 重置战斗时间
        role.status = Status.idle
        transfer_boss()


def battle_task():
    """
    任务
    :return:
    """
    img = screenshot()
    ocrResults = ocr(img)
    if search_text(ocrResults, "吸收"):
        logger_msg("吸收")
        mouse_scroll()
        interactive()
        time.sleep(1)
        return
    now = datetime.now()
    matchOne = False
    for result in ocrResults:
        if "进入" in result.get("text"):
            logger_msg("进入")
            matchOne = True
            select_levels()
            break
        if "推荐等级" in result.get("text"):
            logger_msg("选择等级")
            matchOne = True
            select_levels()
            break
        if "开启挑战" in result.get("text"):
            logger_msg("开启挑战")
            matchOne = True
            click_position(result.get("position"))
            time.sleep(1)
            role.status = Status.fight
            role.fightTime = now
            break
        if "击败" in result.get("text"):
            logger_msg("战斗中")
            matchOne = True
            release_skills()
            role.status = Status.fight
            role.lastFightTime = now
            break
        if "确认" in result.get("text"):
            logger_msg("确认")
            matchOne = True
            control.click(1250 * width_ratio, 650 * height_ratio)
            time.sleep(1)
            break
        if "离开" in result.get("text"):
            logger_msg("离开")
            if search_text(ocrResults, "领取"):
                for i in range(20):
                    forward()
            matchOne = True
            leaving_battle()
            role.status = Status.idle
            break
    if not matchOne and Status.idle:
        logger_msg("前进")
        forward()


def run(func: callable = boss_task):
    """
    运行
    :return:
    """
    logger_msg("线程开始运行")
    global running
    if running:
        return
    running = True
    while running:
        func()
    logger_msg("线程停止运行")


def on_press(key):
    """
    F5 启动
    F6 停止
    F7 退出
    :param key:
    :return:
    """
    global running
    if key == Key.f5:
        logger_msg("启动BOSS脚本")
        thread = Thread(target=run, args=(boss_task,))
        thread.start()
    if key == Key.f6:
        logger_msg("启动无妄者脚本")
        thread = Thread(target=run, args=(battle_task,))
        thread.start()
    if key == Key.f7:
        logger_msg("暂停脚本")
        running = False
    if key == Key.f12:
        logger_msg("退出脚本")
        running = False
        mouse_reset_event.set()
        return False
    return None


if __name__ == "__main__":
    logger_msg("开始运行")
    with Listener(on_press=on_press) as listener:
        listener.join()
    print("结束运行")
