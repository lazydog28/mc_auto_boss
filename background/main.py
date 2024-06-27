import os
import init  # !!此导入删除会导致不会将游戏移动到左上角以及提示当前分辨率!!
import sys
import version
import ctypes
import threading
from mouse_reset import mouse_reset
from multiprocessing import Event, Process
from pynput.keyboard import Key, Listener
from schema import Task
import subprocess
from task import boss_task, synthesis_task, echo_bag_lock_task
from utils import *
from threading import Event as event
from config import config
from read_crashes_data import read_crashes_datas
from collections import OrderedDict
from cmd_line import get_cmd_task_opts


os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
hwnds = win32gui.FindWindow("UnrealWindow", "鸣潮")
app_path = config.AppPath


def restart_app(e: event):
    if app_path:
        while True:
            # 在这里修改重启间隔，单位为秒 time.sleep(7200)表示2个小时重启一次
            # time.sleep(1800)
            # manage_application("UnrealWindow", "鸣潮  ", app_path,e)
            time.sleep(config.GameMonitorTime)  # 每秒检测一次，游戏窗口      改为用户自己设置监控间隔时间，默认为5秒，减少占用(RoseRin)
            find_ue4("UnrealWindow", "UE4-Client Game已崩溃  ")
            find_game_windows("UnrealWindow", "鸣潮  ", e)
            


def find_ue4(class_name, window_title):
    if app_path:
        ue4windows = win32gui.FindWindow(class_name, window_title)
        if ue4windows != 0:  # 检测到游戏发生崩溃-UE4弹窗
            logger("UE4-Client Game已崩溃，尝试重启游戏......")
            win32gui.SendMessage(ue4windows, win32con.WM_CLOSE, 0, 0)
            # 等待崩溃窗口关闭
            time.sleep(2)
            if win32gui.FindWindow(class_name, window_title) == 0:
                return True
        else:
            return False


def find_game_windows(class_name, window_title, taskEvent):
    if app_path:
        gameWindows = win32gui.FindWindow(class_name, window_title)
        if gameWindows == 0:
            logger("未找到游戏窗口")
            while not restart_application(app_path):  # 如果启动失败，则五秒后重新启动游戏窗口
                logger("启动失败，五秒后尝试重新启动...")
            # 运行方法一需要有前提条件
            # 如果重启成功，执行方法一
            time.sleep(20)
            taskEvent.clear()  # 清理BOSS脚本线程(防止多次重启线程占用-导致无法点击进入游戏)
           
            logger("自动启动BOSS脚本")
            thread = Process(target=run, args=(boss_task, taskEvent), name="task")
            thread.start()


def close_window(class_name, window_title):
    # 尝试关闭窗口，如果成功返回 True，否则返回 False
    hwnd = win32gui.FindWindow(class_name, window_title)
    if hwnd != 0:
        win32gui.SendMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        # 等待窗口关闭
        time.sleep(2)
        if win32gui.FindWindow(class_name, window_title) == 0:
            return True
    return False


def restart_application(app_path):
    if app_path:
        time.sleep(5)
        # 尝试启动应用程序，如果成功返回 True，否则返回 False
        try:
            subprocess.Popen(app_path)
            logger("游戏疑似发生崩溃，尝试重启游戏......")
            # 判断文件是否存在，如果存在则删除
            if os.path.exists("isCrashes.txt"):
                os.remove("isCrashes.txt")

            # 重新创建文件并写入值
            with open("isCrashes.txt", "w") as f:
                f.write(str(True))
            return True
        except Exception as e:
            logger(f"启动应用失败: {e}")
            return False


def manage_application(class_name, window_title, app_path, taskEvent):
    if app_path:
        # 先停止脚本
        logger("自动暂停脚本！@")
        taskEvent.clear()
        while True:
            if close_window(class_name, window_title):
                # 如果关闭成功，尝试重启应用程序
                logger("窗口关闭成功，正在尝试重新启动...")
                while not restart_application(app_path):
                    logger("启动失败，五秒后尝试重新启动...")
                # 运行方法一需要有前提条件
                # 如果重启成功，执行方法一
                time.sleep(20)
                logger("自动启动BOSS脚本")
                thread = Process(target=run, args=(boss_task, taskEvent), name="task")
                thread.start()
                break
            else:
                # 如果关闭失败，检查窗口是否还存在
                if win32gui.FindWindow(class_name, window_title) != 0:
                    logger("关闭失败，窗口仍然存在，正在尝试重新关闭...")
                else:
                    logger("窗口已不存在，尝试重启...")
                    while not restart_application(app_path):
                        logger("启动失败，五秒后尝试重新启动...")
                    break


logger(f"初始化完成")


def set_console_title(title: str):
    ctypes.windll.kernel32.SetConsoleTitleW(title)


set_console_title(f"鸣潮自动工具ver {version.__version__}   ---此软件为免费的开源软件 谨防倒卖！")


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
    F5 启动BOSS脚本
    F6 启动融合脚本
    F7 暂停脚本
    F8 启动锁定脚本
    F12 停止脚本
    :param key:
    :return:
    """
    if key == Key.f5:
        logger("启动BOSS脚本")
        thread = Process(target=run, args=(boss_task, taskEvent), name="task")
        thread.start()
    if key == Key.f6:
        logger("启动融合脚本")
        try:
            input(
                "启动融合脚本之前请确保已锁定现有的有用声骸！确定已锁定后按回车继续..."
            )
        except Exception:
            pass
        mouseResetEvent.set()
        time.sleep(1)
        mouse_reset_thread.terminate()
        mouse_reset_thread.join()
        print("")
        thread = Process(target=run, args=(synthesis_task, taskEvent), name="task")
        thread.start()
    if key == Key.f7:
        logger("暂停脚本")
        taskEvent.clear()
    if key == Key.f8:
        logger("启动锁定脚本")
        mouseResetEvent.set()
        time.sleep(1)
        mouse_reset_thread.terminate()
        mouse_reset_thread.join()
        thread = Process(target=run, args=(echo_bag_lock_task, taskEvent), name="task")
        thread.start()
    if key == Key.f12:
        logger("请等待程序退出后再关闭窗口...")
        taskEvent.clear()
        mouseResetEvent.set()
        restart_thread.terminate()
        return False
    return None


# 执行命令行启动任务，todo 多个将异步顺序执行
def run_cmd_tasks_async():
    cmd_task_dict = get_cmd_task_opts()
    if cmd_task_dict is None:
        return
    cmd_keys = ""
    for key_str, keyboard in cmd_task_dict.items():
        cmd_keys += key_str if len(cmd_keys) == 0 else ", " + key_str
    logger("依次执行命令: " + cmd_keys)
    if len(cmd_task_dict) == 1:
        for key_str, keyboard in cmd_task_dict.items():
            on_press(keyboard)
        return
    # 异步 todo F12中断线程
    cmd_task_thread = threading.Thread(target=cmd_task_func, args=(cmd_task_dict,))
    # 守护线程
    cmd_task_thread.daemon = True
    cmd_task_thread.start()


def cmd_task_func(cmd_task_dict: OrderedDict[str, Key]):
    # print(str(cmd_task_dict))
    for key_str, keyboard in cmd_task_dict.items():
        on_press(keyboard)
        # 一键锁定合成刷声骸
        # python background/main.py -t F8,F6,F5 -c config-add-f.yaml
        # todo 暂时只支持单个命令，需等其他功能适配
        # todo F8目前得在背包声骸界面才生效，缺少自动传送到安全点（朔雷右侧），自动打开背包选中声骸栏，进程结束告知执行完
        # todo F6目前得在声骸合成界面才生效，缺少自动传送到安全点（朔雷右侧），自动打开数据坞选中数据融合，进程结束告知执行完
        break


if __name__ == "__main__":
    taskEvent = Event()  # 用于停止任务线程
    mouseResetEvent = Event()  # 用于停止鼠标重置线程
    mouse_reset_thread = Process(
        target=mouse_reset, args=(mouseResetEvent,), name="mouse_reset"
    )
    mouse_reset_thread.start()
    restart_thread = Process(
        target=restart_app, args=(taskEvent,), name="restart_event"
    )
    restart_thread.start()
    if app_path:
        logger(f"游戏路径：{config.AppPath}")
    else:
        logger("未找到游戏路径", "WARN")
    logger("应用重启进程启动")
    logger(f"version: {version.__version__}")
    logger("鼠标重置进程启动")
    print(
        "\n --------------------------------------------------------------"
        "\n     注意：此脚本为免费的开源软件，如果你是通过购买获得的，那么你受骗了！\n "
        "--------------------------------------------------------------\n"
    )
    print("请确认已经配置好了config.yaml文件\n")
    print("使用说明：\n   F5 启动脚本\n   F6 合成声骸\n   F7 暂停运行\n   F8 锁定声骸\n   F12 停止运行")
    logger("开始运行")
    run_cmd_tasks_async()
    with Listener(on_press=on_press) as listener:
        listener.join()
    print("结束运行")
