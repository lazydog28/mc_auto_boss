import time

import init  # !!此导入删除会导致不会将游戏移动到左上角以及提示当前分辨率!!
import threading
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
from config import config
from collections import OrderedDict
from cmd_line import get_cmd_task_opts
from read_crashes_data import is_app_crashes_init
from constant import class_name, window_title


os.environ["KMP_DUPLICATE_LIB_OK"] = "True"
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
app_path = config.AppPath


def restart_app(e: Event):
    if app_path:
        last_check_ue4_timestamp = int(time.time())
        while True:
            # 定时重启功能设置已加入config.yaml(ArcS17)
            if config.RestartWutheringWaves:
                time.sleep(config.RestartWutheringWavesTime)
                manage_application(e)
            # 监测UE4-Client Game已崩溃弹窗，发现就关闭弹窗，干掉游戏进程
            if config.DetectionUE4:
                check_timestamp = ue4_client_crash_monitor(last_check_ue4_timestamp)
                if check_timestamp is not None:
                    last_check_ue4_timestamp = check_timestamp
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
            process = Process(target=run, args=(boss_task, e), name="task")
            process.start()
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
                process = Process(target=run, args=(boss_task, e), name="task")
                process.start()
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
    last_anti_stuck_timestamp = int(time.time())

    last_check_ue4_timestamp = int(time.time())
    if config.DetectionUE4:
        logger("UE4崩溃监测启动")

    while e.is_set():
        # 监测UE4-Client Game已崩溃弹窗，发现就关闭弹窗，干掉游戏进程
        if config.DetectionUE4:
            check_timestamp = ue4_client_crash_monitor(last_check_ue4_timestamp)
            if check_timestamp is not None:
                last_check_ue4_timestamp = check_timestamp

        img = screenshot()
        result = ocr(img)
        try:
            task(img, result)
        except Exception as e:
            try:
                control.activate()
                # 跑向boss会按压按键，出异常及时释放
                control.key_release("w")
                control.key_release(win32con.VK_LSHIFT)
            except Exception:
                pass
            raise
        # 监测游戏是否卡加载，长时间卡在加载界面就干掉游戏进程
        check_timestamp = anti_stuck_monitor(img, anti_stuck_list, last_anti_stuck_timestamp)
        if check_timestamp is not None:
            last_anti_stuck_timestamp = check_timestamp
    logger("进程停止运行")


def on_press(key):
    try:
        key_str = str(key.name).upper()
        if process_dict.get(key_str) is not None and process_dict.get(key_str).is_alive():
            logger(f"{key_str}已启动，不可重复执行")
            return None
    except Exception:
        pass
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
        process = Process(target=run, args=(boss_task, taskEvent), name="task")
        process.start()
        cache_process_dict(key_str, process)
        mouse_reset_process = Process(target=mouse_reset, args=(mouseResetEvent,), name="mouse_reset")
        mouse_reset_process.start()
        cache_process_dict("mouse_reset_process", mouse_reset_process)
    if key == Key.f6:
        logger("启动融合脚本")
        logger("启动融合脚本之前请确保已锁定现有的有用声骸，并确认使用已适配分辨率：\n  1920*1080分辨率1.0缩放\n  1600*900分辨率1.0缩放\n  1368*768分辨率1.0缩放\n  "
               "1280*720分辨率1.5缩放\n  1280*720分辨率1.0缩放\n")
        process = Process(target=run, args=(synthesis_task, taskEvent), name="task")
        process.start()
        cache_process_dict(key_str, process)
        mouse_reset_process = Process(target=mouse_reset, args=(mouseResetEvent,), name="mouse_reset")
        mouse_reset_process.start()
        cache_process_dict("mouse_reset_process", mouse_reset_process)
    if key == Key.f7:
        logger("暂停脚本")
        taskEvent.clear()
        mouseResetEvent.clear()
        force_close_process()
        time.sleep(1)
        logger("暂停执行完成")
    if key == Key.f8:
        logger("启动锁定脚本")
        process = Process(target=run, args=(echo_bag_lock_task, taskEvent), name="task")
        process.start()
        cache_process_dict(key_str, process)
        mouse_reset_process = Process(target=mouse_reset, args=(mouseResetEvent,), name="mouse_reset")
        mouse_reset_process.start()
        cache_process_dict("mouse_reset_process", mouse_reset_process)
    if key == Key.f12:
        logger("请等待程序退出后再关闭窗口...")
        try:
            mc_hwnd = hwnd_util.get_mc_hwnd() # 游戏有崩溃重启过时，主程的hwnd未及时更新不能用，重新获取
            win32gui.PostMessage(mc_hwnd, win32con.WM_KEYUP, ord("w".upper()), 0)
            win32gui.PostMessage(mc_hwnd, win32con.WM_KEYUP, win32con.VK_LSHIFT, 0)
        except Exception:
            pass
        taskEvent.clear()
        mouseResetEvent.clear()
        cmd_event.set()
        # logger(str(process_dict))
        force_close_process()
        restart_process.terminate()
        restart_process.join()
        time.sleep(3)
        logger("程序退出完成")
        time.sleep(0.3)
        return False
    return None


def cache_process_dict(k, v):
    if k in process_dict and process_dict[k] is not None:
        return
    process_dict[k] = v


def force_close_process(name: str = None, timeout: float = 3.0):
    for key, cache_process in process_dict.items():
        try:
            if name is None or key == name:
                if not cache_process.is_alive():
                    continue
                cache_process.terminate()
                cache_process.join(timeout)
        except Exception:
            pass
    process_dict.clear()


# 执行命令行启动任务，多个将异步顺序执行
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
    # 异步
    cmd_task_thread = threading.Thread(target=cmd_task_func, args=(cmd_event, cmd_task_dict))
    # 守护线程
    cmd_task_thread.daemon = True
    cmd_task_thread.start()


def cmd_task_func(cmd_event: threading.Event, cmd_task_dict: OrderedDict[str, Key]):
    # print(str(cmd_task_dict))
    # logger(f"任务线程启动: {cmd_task_dict.keys()}")
    task_size = len(cmd_task_dict)
    for i, (key_str, keyboard) in enumerate(cmd_task_dict.items()):
        # logger(f"i: {i}, size: {task_size}")
        on_press(keyboard)
        if i == task_size - 1:
            break
        # 一键锁定合成刷声骸
        # python background/main.py -t F8,F6,F5 -c config-dreamless.yaml
        while not cmd_event.is_set():
            # logger(f"{str(process_dict)}")
            # logger(f"执行: {key_str}")
            process = process_dict.get(key_str)
            if process is None or process.is_alive():
                # logger("等待")
                time.sleep(5)
                continue
            exitcode = process.exitcode
            if exitcode != 0:
                logger(f"任务{key_str}未正常结束, 返回码: {exitcode}", "WARN")
            break
        on_press(Key.f7)
        time.sleep(3)
    # logger("线程结束")


if __name__ == "__main__":
    taskEvent = Event()  # 用于停止任务线程
    mouseResetEvent = Event()  # 用于停止鼠标重置线程
    restart_process = Process(target=restart_app, args=(taskEvent,), name="restart_event")
    restart_process.start()
    if app_path:
        logger(f"游戏路径：{config.AppPath}")
    else:
        logger("未找到游戏路径", "WARN")
    logger("应用重启进程启动")
    logger(f"version: {version.__version__}")
    logger("鼠标重置进程启动")
    print(
        "\n --------------------------------------------------------------------------"
        "\n     注意：此脚本为免费的开源软件，如果你是通过购买获得的，那么你受骗了！\n "
        "--------------------------------------------------------------------------\n"
    )
    print("请确认已经配置好了config.yaml文件\n")
    print(
        "使用说明：\n   F5  启动脚本\n   F6  合成声骸\n   F7  暂停运行\n   F8  锁定声骸\n   F12 停止运行"
    )
    logger("开始运行")
    process_dict: dict[str, Process] = {}
    cmd_event = threading.Event()
    run_cmd_tasks_async()
    with Listener(on_press=on_press) as listener:
        listener.join()
    logger("结束运行")
    logger("全新GUI预览版，欢迎体验：https://github.com/wakening/WutheringWavesAssistant")
