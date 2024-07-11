import gc
import time
import pytesseract
import win32con
import win32gui
import pyautogui
import cv2
import numpy as np
import re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed  # 导入ThreadPoolExecutor和as_completed，用于并发执行任务
from config import config
from status import info, logger

def isNumber_isloading(keyword, screenshot):
    text = pytesseract.image_to_string(screenshot)
    if re.search(r'\b' + keyword + r'\b', text):
        return True
    else:
        return False






# interval = 0.2  # 默认截图间隔
#创建一个集合来存储已经返回过的文本
returned_texts = set()
last_occurrences = defaultdict(float) #记录第一出现数值的值与时间戳
def isNumber_isloading_disPlays(interval:float):
    """
    检查游戏《鸣潮》的加载进度，以确定是否卡加载进度。

    该函数通过捕获游戏窗口的文本信息，判断加载进度是否达到要求。
    如果加载进度匹配的对应的值超过，则认为游戏卡加载进度，关闭加载窗口，结束检查。
    """
    global returned_texts
    hwnd = win32gui.FindWindow(None, "鸣潮  ")
    while True:    
            try:
                screenshot = capture_window(hwnd, interval)
                # 使用 pytesseract 识别截图中的文字
                text = pytesseract.image_to_string(screenshot)

                # 检查识别到的文字是否包含数字
                if any(char.isdigit() for char in text):
                    # 移除百分号和空格，然后将文本转换为整数
                    filtered_text = ''.join(filter(lambda x: x.isdigit(), text))
                    number = int(filtered_text)
                    # 检查数字是否没有出现在集合内
                    if number not in returned_texts and (1<=number<=100):
                        # 将新的number添加到集合中
                        returned_texts.add(number)
                        # 记录当前识别的数字以及时间戳
                        current_time = time.time()
                        last_occurrences[number]  = current_time
                        logger(f"地图加载进度{number}%","DEBUG")
                        if number == 100:
                                returned_texts.clear() # 清空集合，防止下次出现相同的值，直接判断为超时直接退出游戏
                                last_occurrences.clear()
                                return
                    elif number in returned_texts and (1<=number<=100): # 数字出现在集合内
                           
                        # 检查上次识别的数字是否在6秒内再次出现(其他的情况1-99)
                        # key 表示第1次出现的进度值， value表示第1次出现的进度值的时间
                        for key, value in last_occurrences.items():
                            current_time = time.time()
                            if key == number and current_time - value >= config.ISLoadingTimeout:
                                logger(f"监测到游戏在在{config.ISLoadingTimeout}s内卡在进度{number}%, 关闭游戏","WARN")
                                close_window(None, "鸣潮  ")
                                return        
                                                      
            finally:
                gc.unfreeze()

# 创建一个字典来存储窗口位置和大小的缓存
window_cache = {}

def capture_window(hwnd, interval):
    if hwnd in window_cache:
        left, top, right, bottom = window_cache[hwnd]
    else:
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)  # 获取窗口的位置和大小
        window_cache[hwnd] = (left, top, right, bottom)  # 将结果存入缓存

    width = right - left  # 计算窗口宽度
    height = bottom - top  # 计算窗口高度
    region = None
    if (width >= 1280 and height >= 720):
        region = (right - 250, bottom - 200, 200, 160)  # 截取窗口右下角区域
    elif (width >= 1920 and height >= 1080):
        region = (right - 250, bottom - 200, 240, 140)  # 截取窗口右下角区域

    if region is not None:
        time.sleep(interval)  # 增加延迟-间隔
        screenshot = pyautogui.screenshot(region=region)  # 根据计算出的region截取图片
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)  # 将图片从RGB格式转换为BGR格式
        return screenshot
    else:
        return None

def find_keyword_loading(keyword):
    hwnd = win32gui.FindWindow(None, "鸣潮  ")
    detection_count = config.IsLoadingJueTime  # 检测次数
    right_amount = 0  # 正确次数
    weight = 0.8  # 权重
    for i in range(detection_count):
        screenshot = capture_window(hwnd, 0.2)  # 获取到截取的图片
        if isNumber_isloading(keyword, screenshot):  # 判断是否包含关键词
            right_amount += 1
        time.sleep(1)  # 每秒截图1次
    if right_amount >= round(detection_count * weight):  # 默认8秒中内有6秒检测出10或者75(并发)，则返回True
        return True
    else:
        return False


def check_results():
    keywords = ['10', '75']  # 关键词列表
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(find_keyword_loading, keywords))  # 使用线程池并发搜索关键字
    for result in results:
        if result:
            return True
    return False


# 关闭窗口
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
