import time

import init  # !!此导入删除会导致不会将游戏移动到左上角以及提示当前分辨率!!
import pyautogui
import threading
import sys
import version
import ctypes
from mouse_reset import mouse_reset
from multiprocessing import Event, Process
from pynput.keyboard import Key, Listener
from schema import Task
import subprocess
from task import boss_task, synthesis_task, echo_bag_lock_task, compute_task
from utils import *
from config import config
from collections import OrderedDict
from cmd_line import get_cmd_task_opts
from read_crashes_data import is_app_crashes_init
from constant import class_name, window_title


os.environ["KMP_DUPLICATE_LIB_OK"] = "True"
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
hwnds = win32gui.FindWindow("UnrealWindow", "鸣潮")
app_path = config.AppPath
# 崩溃的图片，在项目根目录
IMAGE_NAME_UE4_CRASH = os.path.join(config.project_root, "message.png")


# 关闭UE4崩溃弹窗
def find_and_press_enter():
    while True:
        try:
            x, y = pyautogui.locateCenterOnScreen(IMAGE_NAME_UE4_CRASH, confidence=0.8)
            if x is not None and y is not None:
                time.sleep(1)
                pyautogui.press("enter")
        except Exception:
            time.sleep(config.UE4_POPUP)


def restart_app(e: Event):
    if app_path:
        while True:
            # 定时重启功能设置已加入config.yaml(ArcS17)
            if config.RestartWutheringWaves:
                time.sleep(config.RestartWutheringWavesTime)
                manage_application(e)
            # 每秒检测一次，游戏窗口   改为用户自己设置监控间隔时间，默认为5秒，减少占用(RoseRin)
            time.sleep(config.GameMonitorTime)
            find_game_windows(e)


def find_game_windows(e: Event):
    if app_path:
        gameWindows = win32gui.FindWindow(class_name, window_title)
        # 没有检测到游戏窗口
        if gameWindows == 0:
            logger("未找到游戏窗口")
            while not restart_application():  # 如果启动失败，则五秒后重新启动游戏窗口
                logger("启动失败，五秒后尝试重新启动...")
            # 运行方法一需要有前提条件
            # 如果重启成功，执行方法一
            time.sleep(15)
            e.clear()  # 清理BOSS脚本线程(防止多次重启线程占用-导致无法点击进入游戏)
            logger("自动启动BOSS脚本")
            # 增加重启线程延时避免重启游戏加载过程中仍无法截取游戏窗口(ArcS17)
            time.sleep(10)
            thread = Process(target=run, args=(boss_task, e), name="task")
            thread.start()
        else:
            # 检查到游戏窗口
            # 这段代码的功能是检查一个名为 "isCrashes.txt" 的文件是否存在于项目的根目录下。
            # 如果文件存在，它会读取文件内容并判断是否为 "True" 或 "False"。
            # 如果文件不存在，它会创建一个新文件并写入 "True 或者 False，通过isFileExist_TORF传入"。
            is_app_crashes_init(False)


def close_window():
    # 尝试关闭窗口，如果成功返回 True，否则返回 False
    if win32gui.FindWindow(class_name, window_title) != 0:
        win32gui.SendMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        # 等待窗口关闭
        time.sleep(2)
        if win32gui.FindWindow(class_name, window_title) == 0:
            return True
    return False


def restart_application():
    if app_path:
        time.sleep(5)
        # 尝试启动应用程序，如果成功返回 True，否则返回 False
        try:
            subprocess.Popen(app_path)
            logger("游戏疑似发生崩溃或自动关闭，尝试重启游戏...")
            # 判断根目录文件isCrashes.txt是否存在，如果存在则删除
            is_crashes_file = os.path.join(config.project_root, "isCrashes.txt")
            if os.path.exists("isCrashes.txt"):
                os.remove(is_crashes_file)

            # 重新创建文件并写入值
            with open(is_crashes_file, "w") as f:
                f.write(str(True))
            return True
        except Exception as e:
            logger(f"启动应用失败: {e}")
            return False


def manage_application(e: Event):
    if app_path:
        # 先停止脚本
        logger("自动暂停脚本！")
        e.clear()
        while True:
            if close_window():
                # 如果关闭成功，尝试重启应用程序
                logger("窗口关闭成功，正在尝试重新启动...")
                while not restart_application():
                    logger("启动失败，五秒后尝试重新启动...")
                # 运行方法一需要有前提条件
                # 如果重启成功，执行方法一
                time.sleep(20)
                logger("自动启动BOSS脚本")
                thread = Process(target=run, args=(boss_task, e), name="task")
                thread.start()
                break
            else:
                # 如果关闭失败，检查窗口是否还存在
                if win32gui.FindWindow(class_name, window_title) != 0:
                    logger("关闭失败，窗口仍然存在，正在尝试重新关闭...")
                else:
                    logger("窗口已不存在，尝试重启...")
                    while not restart_application():
                        logger("启动失败，五秒后尝试重新启动...")
                    break


logger(f"初始化完成")


def set_console_title(title: str):
    ctypes.windll.kernel32.SetConsoleTitleW(title)


set_console_title(
    f"鸣潮自动工具ver {version.__version__}   ---此软件为免费的开源软件 谨防倒卖！"
)


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

    logger("卡加载监测启动")
    anti_stuck_list = []
    last_timestamp = int(time.time())

    while e.is_set():
        img = screenshot()
        result = ocr(img)
        task(img, result)

        # 监测游戏是否卡加载，长时间卡在加载界面就干掉游戏进程
        check_timestamp = anti_stuck_monitor(img, anti_stuck_list, last_timestamp)
        if check_timestamp is not None:
            last_timestamp = check_timestamp
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
                "启动融合脚本之前请确保已锁定现有的有用声骸，并确认使用已适配分辨率：\n  1920*1080分辨率1.0缩放\n  1600*900分辨率1.0缩放\n  1368*768分辨率1.0缩放\n  "
                "1280*720分辨率1.5缩放\n  1280*720分辨率1.0缩放\n  回车确认 Enter..."
            )
        except:
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
    if key == Key.f9:
        logger("声骇得分计算启动，请确认当前处于角色声骇详情页","WARN")
        try:
            input(
                "\n         计算需要在角色声骇详情页面进行，否则将无法识别"
                "\n         前往顺序为 按下C-> 属性详情-> 声骇-> 点击右侧声骇，请确保处于该页面，否则将无法识别"
                "\n         目前仅适配1920*1080分辨率    回车确认 Enter..."
            )
                
        # except:
        #     pass
        except Exception as e:
            logger(f"发生错误: {e}", "ERROR")
            taskEvent.clear()
            mouseResetEvent.set()
            restart_thread.terminate()  # 杀死默认开启状态的检测窗口的线程
            sys.exit(1)
        thread = Process(target=run, args=(compute_task, taskEvent), name="task")
        thread.start()
    if key == Key.f12:
        logger("请等待程序退出后再关闭窗口...")
        taskEvent.clear()
        mouseResetEvent.set()
        restart_thread.terminate()  # 杀死默认开启状态的检测窗口的线程
        if config.DetectionUE4:  # 检测UE4窗口崩溃时开启状态的时候，才杀死该线程
            find_crash_popup_thread.terminate()
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

    if config.DetectionUE4:
        # 创建并启动线程-检查UE4崩溃弹窗
        find_crash_popup_thread = Process(target=find_and_press_enter)
        find_crash_popup_thread.start()
    if app_path:
        logger(f"游戏路径：{config.AppPath}")
    else:
        logger("未找到游戏路径", "WARN")
    logger("应用重启进程启动")
    logger(f"version: {version.__version__}")
    logger("鼠标重置进程启动")
    print(
        "\n ------------------------------------------------------------------------"
        "\n     注意：此脚本为免费的开源软件，如果你是通过购买获得的，那么你受骗了！\n "
        "------------------------------------------------------------------------\n"
    )
    print("请确认已经配置好了config.yaml文件\n")
    print(
        "使用说明：\n   F5  启动脚本\n   F6  合成声骸\n   F7  暂停运行\n   F8  锁定声骸\n   F9  声骇得分计算\n   F12 停止运行"
    )
    logger("开始运行")
    run_cmd_tasks_async()
    with Listener(on_press=on_press) as listener:
        listener.join()
    print("结束运行")
