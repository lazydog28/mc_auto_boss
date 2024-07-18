# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: constant.py
@time: 2024/6/5 上午8:24
@author SuperLazyDog
"""
import ctypes
import time
import win32gui
import sys
import subprocess
import os
import re
from ctypes import windll


def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0


def get_scale_factor():
    try:
        windll.shcore.SetProcessDpiAwareness(1)  # 设置进程的 DPI 感知
        scale_factor = windll.shcore.GetScaleFactorForDevice(
            0
        )  # 获取主显示器的缩放因子
        return scale_factor / 100  # 返回百分比形式的缩放因子
    except Exception as e:
        print("Error:", e)
        return None


def wait_exit():
    input("按任意键退出...")
    sys.exit(0)


def check_game_resolution():
    from config import config
    valid_resolutions = [
        [1280, 720],
        [1366, 768],
        [1440, 900],
        [1600, 900],
        [1920, 1080],
        [1920, 1200],
        [2560, 1440],
        [3840, 2160]
    ]
    if config.GameResolution and len(config.GameResolution) == 2:
        if config.GameResolution in valid_resolutions:
            game_resolution_x = config.GameResolution[0]
            game_resolution_y = config.GameResolution[1]
            print(f"分辨率检查完毕，将使用分辨率{game_resolution_x}, {game_resolution_y}启动游戏")
            return game_resolution_x, game_resolution_y
        else:
            print(f"分辨率{config.GameResolution}不在可使用范围内，请检查配置文件，将使用游戏默认配置启动游戏")
    return None, None

# 通过Client-Win64-Shipping.exe调用启动参数可不修改配置文件
# def set_game_config_resolution(game_resolution_x, game_resolution_y):
#     from config import config
#     game_path = os.path.dirname(config.AppPath)
#     game_config_file_path = os.path.join(game_path, "Client/Saved/Config/WindowsNoEditor/GameUserSettings.ini")
#     with open(game_config_file_path, 'r') as file:
#         lines = file.readlines()
#     for i, line in enumerate(lines):
#         if line.startswith('ResolutionSizeX='):
#             lines[i] = f'ResolutionSizeX={game_resolution_x}\n'
#         elif line.startswith('ResolutionSizeY='):
#             lines[i] = f'ResolutionSizeY={game_resolution_y}\n'
#         elif line.startswith('LastUserConfirmedResolutionSizeX='):
#             lines[i] = f'LastUserConfirmedResolutionSizeX={game_resolution_x}\n'
#         elif line.startswith('LastUserConfirmedResolutionSizeY='):
#             lines[i] = f'LastUserConfirmedResolutionSizeY={game_resolution_y}\n'
#     with open(game_config_file_path, 'w') as file:
#         file.writelines(lines)


def get_game_path():
    from config import config
    game_path = os.path.join(os.path.dirname(config.AppPath), "Client/Binaries/Win64/Client-Win64-Shipping.exe")
    return game_path


def game_start(none_log: bool = False):
    from config import config
    app_path = config.AppPath
    game_path = get_game_path()
    print("\n")
    if app_path:
        try:
            if not none_log:
                print("未检测到游戏窗口，尝试启动游戏")
            game_resolution_x, game_resolution_y = check_game_resolution()
            if game_resolution_x and game_resolution_y:
                # print(f"修改游戏配置分辨率为{game_resolution_x}, {game_resolution_y}")  # 无需设置游戏配置文件
                # set_game_config_resolution(game_resolution_x, game_resolution_y)  # 无需设置配置文件
                arguments = [f"-ResX={game_resolution_x}", f"-ResY={game_resolution_y}", "-windowed", "-nosound"]
                print(f"以{game_resolution_x}, {game_resolution_y}分辨率启动游戏")
                subprocess.Popen([game_path] + arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, start_new_session=True)
            else:
                subprocess.Popen(game_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, start_new_session=True)
        except Exception:
            if not none_log:
                print("游戏路径设置错误，无法启动游戏")


if not is_admin():
    print("请以管理员权限运行此程序")
    wait_exit()
hwnd = win32gui.FindWindow("UnrealWindow", "鸣潮  ")
if hwnd == 0:
    game_start()
    time.sleep(10)
    hwnd = win32gui.FindWindow("UnrealWindow", "鸣潮  ")
    if hwnd == 0:
        print("启动游戏失败，按任意键退出")
        wait_exit()
left, top, right, bot = win32gui.GetClientRect(hwnd)
w = right - left
h = bot - top
scale_factor = get_scale_factor()
width_ratio = w / 1920 * scale_factor
height_ratio = h / 1080 * scale_factor
real_w = int(w * scale_factor)
real_h = int(h * scale_factor)
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 判断 root_path 中是否包含中文或特殊字符
special_chars_pattern = r"[\u4e00-\u9fa5\!\@\#\$\%\^\&\*\(\)]"
if bool(re.search(special_chars_pattern, root_path)):
    print("请将项目路径移动到纯英文路径下")
    wait_exit()
