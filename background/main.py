import os
import time
import init  # !!此导入删除会导致不会将游戏移动到左上角以及提示当前分辨率!!
import sys
import version
import ctypes
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
        is_crashes_file = os.path.join(config.project_root, "isCrashes.txt")
        is_game_restarting_file = os.path.join(config.project_root, "isRestarting.dat")
        # 尝试启动应用程序，如果成功返回 True，否则返回 False
        try:
            subprocess.Popen(app_path)
            logger("游戏疑似发生崩溃，尝试重启游戏......")
            # 判断文件是否存在，如果存在则删除
            if os.path.exists(is_crashes_file):
                os.remove(is_crashes_file)
            # 重新创建文件并写入值
            with open(is_crashes_file, "w") as f:
                f.write(str(True))
            with open(is_game_restarting_file, "w") as f:
                f.write(str("Restarting"))
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


set_console_title(f"McTool ver {version.__version__}   ---RinRin自用版本")


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
        thread = Process(target=run, args=(synthesis_task, taskEvent), name="task")
        end_thread(mouseResetEvent, mouse_reset_thread)
        thread.start()
    if key == Key.f7:
        logger("暂停脚本")
        taskEvent.clear()
    if key == Key.f8:
        logger("启动锁定脚本")
        thread = Process(target=run, args=(echo_bag_lock_task, taskEvent), name="task")
        thread.start()
        end_thread(mouseResetEvent, mouse_reset_thread)
    if key == Key.f12:
        logger("请等待程序退出后再关闭窗口...")
        taskEvent.clear()
        mouseResetEvent.set()
        restart_thread.terminate()
        return False
    return None


def check_confirm_user_permissions():
    user_level = "RinRin"
    secret_key = "957222395"  # 设置启动密钥
    if user_level == "RinRin":
        user_input = "RinRin95"
    else:
        user_input = input("\n请输入启动密钥：")
    if user_input == secret_key:
        print("密钥正确，程序启动。")
        confirm = True
    elif user_input == "RinRin95":
        print("☆RinRin☆")
        confirm = True
    else:
        print("密钥错误，程序退出。")
        confirm = False
    return confirm
    # 在这里添加你的程序逻辑


def check_authorization_validity_period():
    validity_time = datetime(2024, 7, 15, 0, 0, 0)
    print(f"授权有效期至{validity_time.year}/{validity_time.month}/{validity_time.day} {validity_time.hour}:{validity_time.minute}:{validity_time.second}")
    remaining_time = validity_time - datetime.now()
    if remaining_time.total_seconds() < 0:
        print("授权已过期")
        return False
    else:
        days = remaining_time.days
        hours, remainder = divmod(remaining_time.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        print(f"验证成功，剩余{days}天{hours}小时{minutes}分钟。")
        return True


def end_thread(thread_name, thread):
    thread_name.set()
    time.sleep(1)
    thread.join()


if __name__ == "__main__":
    user = "guest"
    if user == "Rin":
        pass
    else:
        if not check_authorization_validity_period():
            time.sleep(3)
            exit()
        if not check_confirm_user_permissions():
            time.sleep(3)
            exit()
    # 在这里添加你的程序逻辑
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
        "\n     注意：此版本为RinRin自用版本，如你获得此代码，请立即删除！\n "
        "--------------------------------------------------------------\n"
    )
    print("请确认已经配置好了config.yaml文件\n")
    print("使用说明：\n   F5 启动脚本\n   F6 合成声骸\n   F7 暂停运行\n   F8 锁定声骸\n   F12 停止运行")
    logger("开始运行")
    with Listener(on_press=on_press) as listener:
        listener.join()
    print("结束运行")
