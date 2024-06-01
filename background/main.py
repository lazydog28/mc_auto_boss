from utils import screenshot, ocr, search_text
import time
from datetime import datetime
from pynput.keyboard import Listener, Key
from threading import Thread
from operation import (
    interactive,
    release_skills,
    click_position,
    mouse_scroll,
    transfer_beacon,
    control,
)
from config import config

running = False
inBattle = False
noBossTime = time.time()
bossTime = time.time()
lastMsg = ""


def logger_msg(msg: str):
    global lastMsg
    now = time.time()
    content = (
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
        f"战斗时长：{int(now - bossTime):<4}秒 "
        f"非战斗时长：{int(now - noBossTime):<4}秒  "
        f"{msg}"
    )
    start = "\n" if lastMsg != msg else "\r"
    content = start + content
    print(content, end="")
    lastMsg = msg


logger_msg("初始化完成")


def boss_task():
    global noBossTime, bossTime
    img = screenshot()
    ocrResults = ocr(img)
    if search_text(ocrResults, "吸收"):
        logger_msg("吸收")
        mouse_scroll()
        interactive()
        time.sleep(1)
        return
    now = time.time()
    for item in ocrResults:
        if "击败" in item.get("text"):
            logger_msg("战斗中")
            release_skills()
            noBossTime = now
        if "取消" in item.get("text"):
            logger_msg("取消")
            click_position(item.get("position"))
            break
        if "终端" in item.get("text"):
            logger_msg("终端")
            control.esc()
            time.sleep(1)
    if (now - noBossTime) > 5:
        logger_msg("非战斗状态")
        bossTime = now
    if now - noBossTime > config.MaxNoBossTime:
        logger_msg("长时间处于非战斗状态 传送")
        noBossTime = now
        transfer_beacon()
    if now - bossTime > config.MaxBossTime:
        logger_msg("长时间处于战斗状态 传送")
        bossTime = now
        transfer_beacon()


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
