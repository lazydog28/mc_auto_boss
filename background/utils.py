# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: utils.py
@time: 2024/5/26 下午8:59
@author SuperLazyDog
"""
from ctypes import windll
from typing import List, Dict, Any
import win32ui
import numpy as np
import sys
import cv2
from paddleocr import PaddleOCR
from datetime import datetime
import win32gui
import os
from paddle.device import is_compiled_with_cuda
from config import role
from multiprocessing import current_process
import re


def logger_msg(msg: str):
    global lastMsg
    content = (
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
        f"当前角色状态：{role.status} "
        f"{msg}"
    )
    start = "\n" if lastMsg != msg else "\r"
    content = start + content
    print(content, end="")
    lastMsg = msg


def screenshot() -> np.ndarray | None:
    """
    截取当前窗口的屏幕图像。

    通过调用Windows图形设备接口（GDI）和Python的win32gui、win32ui模块，
    本函数截取指定窗口的图像，并将其存储为numpy数组。

    返回值:
        - np.ndarray: 截图的numpy数组，格式为RGB（不包含alpha通道）。
        - None: 如果截取屏幕失败，则返回None。
    """
    hwndDC = win32gui.GetWindowDC(hwnd)  # 获取窗口设备上下文（DC）
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)  # 创建MFC DC从hwndDC
    saveDC = mfcDC.CreateCompatibleDC()  # 创建与mfcDC兼容的DC
    saveBitMap = win32ui.CreateBitmap()  # 创建一个位图对象
    saveBitMap.CreateCompatibleBitmap(mfcDC, real_w, real_h)  # 创建与mfcDC兼容的位图
    saveDC.SelectObject(saveBitMap)  # 选择saveDC的位图对象，准备绘图

    # 尝试使用PrintWindow函数截取窗口图像
    result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)
    if result != 1:
        logger_msg("截取屏幕失败")
        return screenshot()  # 如果截取失败，则重试

    # 从位图中获取图像数据
    bmp_info = saveBitMap.GetInfo()  # 获取位图信息
    bmp_str = saveBitMap.GetBitmapBits(True)  # 获取位图数据
    im = np.frombuffer(bmp_str, dtype="uint8")  # 将位图数据转换为numpy数组
    im.shape = (bmp_info["bmHeight"], bmp_info["bmWidth"], 4)  # 设置数组形状
    im = im[:, :, [2, 1, 0, 3]]  # 调整颜色通道顺序为RGB

    # 清理资源
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    return im  # 返回截取到的图像


def ocr(img: np.ndarray) -> List[Dict[str, Any]]:
    results = ocrIns.ocr(img, cls=False)
    if len(results) == 0:
        return []
    results = results[0]
    if results is None:
        return []
    res = []
    for result in results:
        text = result[1][0]
        position = result[0]
        res.append({"text": text, "position": position})
    return res


def matchTemplate(
        img: np.ndarray, template: np.ndarray, threshold: float = 0.8
) -> None | Dict[str, Any]:
    """
    使用 opencv matchTemplate 方法 模板匹配 返回匹配结果
    :param img:  大图片
    :param template: 小图片
    :param threshold:  阈值
    :return:
    """
    # 判断是否为灰度图，如果不是转换为灰度图
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if len(template.shape) == 3:
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # 将  template 进行缩放
    template = cv2.resize(template, (0, 0), fx=width_ratio, fy=height_ratio)

    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    confidence = np.max(res)
    if confidence < threshold:
        return None
    maxLoc = np.where(res == confidence)
    return {
        "x": maxLoc[1][0] + template.shape[1] // 2,
        "y": maxLoc[0][0] + template.shape[0] // 2,
        "w": template.shape[1],
        "h": template.shape[0],
        "confidence": confidence,
    }


rare_chars = "鸷"


def search_text(results: List[Dict[str, Any]], target: str) -> Dict[str, Any] | None:
    target = re.sub(rf"[{rare_chars}]", ".", target)  # 判断 target 是否包含生僻字，如果包含则使用正则将生僻字替换为任意字符
    for result in results:
        if re.search(target, result.get("text")): # 使用正则匹配
            return result
    return None


def wait_text(targets: str | list[str], timeout: int = 3) -> Dict[str, Any] | None:
    start = datetime.now()
    if isinstance(targets, str):
        targets = [targets]
    while True:
        img = screenshot()
        if img is None:
            continue
        if (datetime.now() - start).seconds > timeout:
            return None
        result = ocr(img)
        for target in targets:
            if text_info := search_text(result, target):
                return text_info
    return None


def find_text(targets: str | list[str]) -> Dict[str, Any] | None:
    if isinstance(targets, str):
        targets = [targets]
    img = screenshot()
    if img is None:
        return None
    result = ocr(img)
    for target in targets:
        if text_info := search_text(result, target):
            return text_info
    return None


def get_scale_factor():
    try:
        windll.shcore.SetProcessDpiAwareness(1)  # 设置进程的 DPI 感知
        scale_factor = windll.shcore.GetScaleFactorForDevice(0)  # 获取主显示器的缩放因子
        return scale_factor / 100  # 返回百分比形式的缩放因子
    except Exception as e:
        print("Error:", e)
        return None


lastMsg = ""
hwnd = win32gui.FindWindow("UnrealWindow", "鸣潮  ")
if hwnd == 0:
    logger_msg("未找到游戏窗口")
    sys.exit(1)
left, top, right, bot = win32gui.GetClientRect(hwnd)
w = right - left
h = bot - top
scale_factor = get_scale_factor()
if scale_factor is None:
    logger_msg("获取屏幕缩放失败")
    sys.exit(1)
real_w = int(w * scale_factor)
real_h = int(h * scale_factor)
# 设置窗口位置为0,0
width_ratio = w / 1920 * scale_factor
height_ratio = h / 1080 * scale_factor
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 判断 root_path 中是否包含中文或特殊字符
special_chars_pattern = r'[\u4e00-\u9fa5\!\@\#\$\%\^\&\*\(\)]'
if bool(re.search(special_chars_pattern, root_path)):
    logger_msg("请将项目路径移动到纯英文路径下")
    sys.exit(1)
if current_process().name == "task":
    logger_msg("初始化中")
    logger_msg(f"窗口大小：{w}x{h} 当前屏幕缩放：{scale_factor} 游戏分辨率：{real_w}x{real_h}")
    logger_msg(f"项目路径：{root_path}")
    # 获取项目根目录 根目录为当前文件的上一级目录
    det_model_dir = os.path.join(root_path, "models/det/ch/ch_PP-OCRv4_det_infer")
    rec_model_dir = os.path.join(root_path, "models/rec/ch/ch_PP-OCRv4_rec_infer")
    if is_compiled_with_cuda():
        ocrIns = PaddleOCR(
            lang="ch",
            use_gpu=True,
            show_log=False,
            det_model_dir=det_model_dir,
            rec_model_dir=rec_model_dir,
        )
        logger_msg("使用GPU加速OCR识别")
    else:
        ocrIns = PaddleOCR(
            lang="ch",
            use_gpu=False,
            show_log=False,
            det_model_dir=det_model_dir,
            rec_model_dir=rec_model_dir,
        )
        logger_msg("使用CPU进行OCR识别")
    rect = win32gui.GetWindowRect(hwnd)  # 获取窗口区域
    win32gui.MoveWindow(
        hwnd, 0, 0, rect[2] - rect[0], rect[3] - rect[1], True
    )  # 设置窗口位置为0,0
