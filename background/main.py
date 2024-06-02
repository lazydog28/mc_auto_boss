from utils import screenshot, ocr, search_text
import time
from pynput.keyboard import Listener, Key
from threading import Thread
from utils import logger_msg
from operation import (
    interactive,
    release_skills,
    click_position,
    mouse_scroll,
    transfer_boss,
    control,
)
from config import config, role, Status
from datetime import datetime

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
    for item in ocrResults:
        if "击败" in item.get("text"):
            logger_msg("战斗中")
            release_skills()
            if role.status == Status.idle:
                role.fightTime = now
            role.status = Status.fight
            role.lastFightTime = now
        if "取消" in item.get("text"):
            logger_msg("取消")
            click_position(item.get("position"))
            break
        if "终端" in item.get("text"):
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

    if key == Key.f5:
        logger_msg("启动BOSS脚本")
        thread = Thread(target=run)
        thread.start()
    if key == Key.f7:
        logger_msg("停止脚本")
        global running
        running = False
    if key == Key.f12:
        logger_msg("退出脚本")
        return False
    return None


if __name__ == "__main__":
    logger_msg("开始运行")
    with Listener(on_press=on_press) as listener:
        listener.join()
    print("结束运行")
