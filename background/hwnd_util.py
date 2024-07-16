"""
windows窗口工具

@software: PyCharm
@file: hwnd_util.py
@time: 2024/7/06 下午1:00
@author wakening
"""
import re
import psutil
import win32gui
import win32process

# 纯粹的窗口工具脚本，只可被其他脚本引用，不要在此引入其他自己写的包，
# 会带入各种全局变量和逻辑造成影响，也不要在这写逻辑（去utils.py写） by wakening
# from status import logger

# mc相关进程
client_win64_shipping_exe = "Client-Win64-Shipping.exe"  # 登录客户端
wuthering_waves_exe = "Wuthering Waves.exe"  # 游戏主程序
launcher_exe = "launcher.exe"  # 启动器

# mc窗口相关属性
mc_hwnd_class_name = "UnrealWindow"
mc_hwnd_title = "鸣潮  "
# 国服登录窗口
official_login_hwnd_class_name = "#32770"
official_login_hwnd_title = ""
# b服登录窗口
bilibili_login_hwnd_class_name = "CLoginDlg_P_8340_\\d{10}"  # CLoginDlg_P_8340_1720374432
bilibili_login_hwnd_title = "bilibili游戏 登录_弹框"


def get_pid_by_exe_name(exe_name: str):
    for proc in psutil.process_iter(['name', 'pid']):
        if proc.info['name'] == exe_name:
            pro_pid = proc.info['pid']
            # print(f"pid: {pro_pid}")
            return pro_pid
    return None


# 获取当前系统所有窗口句柄
def get_all_hwnd() -> list:
    def get_hwnd_callback(cb_hwnd, cb_window_list):
        # _, found_pid = win32process.GetWindowThreadProcessId(cb_hwnd)
        # print(f"found_pid: {found_pid}")
        cb_window_list.append(cb_hwnd)

    window_list: list = []
    win32gui.EnumWindows(get_hwnd_callback, window_list)
    return window_list


def get_hwnd_by_exe_name(exe_name: str) -> list | None:
    ge_pid = get_pid_by_exe_name(exe_name)
    if ge_pid is None:
        return None
    ge_hwnd_list: list = get_all_hwnd()
    rt_hwnd_list: list = []
    for ge_hwnd in ge_hwnd_list:
        _, found_pid = win32process.GetWindowThreadProcessId(ge_hwnd)
        if found_pid == ge_pid:
            rt_hwnd_list.append(ge_hwnd)
    return rt_hwnd_list


def get_hwnd_by_class_and_title(class_name: str, title: str):
    return win32gui.FindWindow(class_name, title)


# 获取mc游戏窗口句柄
def get_mc_hwnd():
    return get_hwnd_by_class_and_title(mc_hwnd_class_name, mc_hwnd_title)


# 官服 获取账号登录界面窗口句柄 by wakening
def get_login_hwnd_official() -> list | None:
    wd_hwnd_list = get_hwnd_by_exe_name(client_win64_shipping_exe)
    if wd_hwnd_list is None or len(wd_hwnd_list) == 0:
        return None
    login_hwnd_list = []
    for wd_hwnd in wd_hwnd_list:
        if win32gui.IsWindow(wd_hwnd) and win32gui.IsWindowEnabled(wd_hwnd) and win32gui.IsWindowVisible(wd_hwnd):
            window_class = win32gui.GetClassName(wd_hwnd)
            # print(f"window: {wd_hwnd}, window class: {window_class}, title: {win32gui.GetWindowText(wd_hwnd)}")
            # window class: UnrealWindow, title: 鸣潮
            # window class: #32770, title:
            # 目前游戏v1.1版本有游戏本体窗口，账号登录窗口等
            # 账号登录窗口没有标题，类名#32770不确定是否会变，无法准确定位
            # 考虑到后续窗口可能变多，返回数组 by wakening
            if window_class != mc_hwnd_class_name:
                login_hwnd_list.append(wd_hwnd)
    return login_hwnd_list


# b服 获取账号登录界面窗口句柄 by wakening
def get_login_hwnd_bilibili():
    windows_list: list = get_all_hwnd()
    for wd_hwnd in windows_list:
        window_class = win32gui.GetClassName(wd_hwnd)
        pattern = re.compile(rf"^{bilibili_login_hwnd_class_name}$")
        match = pattern.match(window_class)
        if match:
            # print(f"window class: {window_class}, title: {win32gui.GetWindowText(wd_hwnd)}")
            return wd_hwnd
    return None
