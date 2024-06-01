from utils import screenshot, ocr, search_text
import time
from datetime import datetime
from pynput.keyboard import Listener, Key
from threading import Thread
from operation import (
    interactive,
    select_levels,
    click,
    release_skills,
    leaving_battle,
    forward,
    click_position,
    mouse_scroll,
    transfer_beacon,
    keyboard,
)

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


def battle_task():
    """
    任务
    :return:
    """
    global inBattle
    img = screenshot()
    results = ocr(img)
    resultText = [item.get("text") for item in results if len(item.get("text")) >= 2]
    matchOne = False
    if "吸收" in resultText:
        logger_msg("吸收")
        matchOne = True
        interactive()
        time.sleep(1)
    for text in resultText:
        if "吸收" in text:
            logger_msg("吸收")
            matchOne = True
            interactive()
            break
        if "进入" in text:
            logger_msg("进入")
            matchOne = True
            interactive()
        if "推荐等级" in text:
            logger_msg("选择等级")
            matchOne = True
            select_levels()
            break
        if "开启挑战" in text:
            logger_msg("开启挑战")
            matchOne = True
            click(1500, 1000)
            time.sleep(1)
            inBattle = True
            break
        if "击败" in text:
            logger_msg("战斗中")
            matchOne = True
            release_skills()
            break
        if "确认" in text:
            logger_msg("确认")
            matchOne = True
            click(1250, 650)
            time.sleep(1)
            inBattle = False
            break
        if "离开" in text:
            logger_msg("离开")
            if search_text(results, "领取"):
                for i in range(20):
                    forward()
            matchOne = True
            leaving_battle()
            break
    if not matchOne and not inBattle:
        logger_msg("前进")
        forward()


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
            keyboard.tap(Key.esc)
            time.sleep(1)
    if (now - noBossTime) > 3:
        logger_msg("非战斗状态")
        bossTime = now
    if now - noBossTime > 60:
        logger_msg("传送")
        noBossTime = now
        transfer_beacon()
    if now - bossTime > 120:
        logger_msg("长时间处于战斗状态 传送")
        bossTime = now
        transfer_beacon()


def run(func: callable = battle_task):
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
        logger_msg("启动秘境脚本")
        thread = Thread(target=run)
        thread.start()
    if key == Key.f6:
        logger_msg("启动BOSS脚本")
        thread = Thread(target=run, args=(boss_task,))
        thread.start()
    if key == Key.f7:
        logger_msg("停止脚本")
        global running
        running = False
    if key == Key.f12:
        logger_msg("退出脚本")
        return False


if __name__ == "__main__":
    logger_msg("开始运行")
    with Listener(on_press=on_press) as listener:
        listener.join()
    print("结束运行")
