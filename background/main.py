import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import init
from mouse_reset import mouse_reset
from multiprocessing import Event, Process
from status import logger
from pynput.keyboard import Key, Listener
from schema import Task
from task import boss_task, synthesis_task
from ocr import ocr
from utils import screenshot

logger(f"初始化完成")


def run(task: Task, e: Event):
    """
    运行
    :return:
    """
    logger("任务进程开始运行")
    logger("请将鼠标移出游戏窗口，避免干扰脚本运行")
    if e.is_set():
        logger("任务进程已经在运行，不需要再次启动")
        return
    e.set()
    while e.is_set():
        img = screenshot()
        result = ocr(img)
        task(img, result)
    logger("进程停止运行")


def on_press(key):
    """
    F5 启动
    F6 停止
    F7 退出
    :param key:
    :return:
    """
    if key == Key.f5:
        logger("启动BOSS脚本")
        thread = Process(target=run, args=(boss_task, taskEvent), name="task")
        thread.start()
    if key == Key.f6:
        logger("启动融合脚本")
        print("")
        print("https://hermes981128.oss-cn-shanghai.aliyuncs.com/ImageBed/1717865624102.png")
        try:
            input(
                "启动融合脚本之前请确保已筛选声骸品质，避免将五星声骸被合成！确定已筛选后按回车继续..."
            )
        except Exception:
            pass
        print("")
        thread = Process(target=run, args=(synthesis_task, taskEvent), name="task")
        thread.start()
    if key == Key.f7:
        logger("暂停脚本")
        taskEvent.clear()
    if key == Key.f12:
        logger("请等待程序退出后再关闭窗口...")
        taskEvent.clear()
        mouseResetEvent.set()
        return False
    return None


if __name__ == "__main__":
    taskEvent = Event()  # 用于停止任务线程
    mouseResetEvent = Event()  # 用于停止鼠标重置线程
    mouse_reset_thread = Process(
        target=mouse_reset, args=(mouseResetEvent,), name="mouse_reset"
    )
    mouse_reset_thread.start()
    logger("鼠标重置进程启动")
    logger("开始运行")
    with Listener(on_press=on_press) as listener:
        listener.join()
    print("结束运行")
