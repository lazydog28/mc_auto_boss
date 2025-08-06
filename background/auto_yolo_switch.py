import os
from status import logger
from config import config
from yolo import switch_model

default_yolo_logger = "使用【默认】模型进行识别"  # 默认模型的log日志
ModelName_ext = ".onnx"  # 模型文件的后缀名

# 模型文件名称
defaultModelName = "yolo"  # 默认1.0全boss
boss_v20 = "boss_v20"  # 2.0全boss + 无妄者 + 角

# 作用：将模型独立分开，易于定位分析问题与维护
# 根据boss名称动态的切换模型，
def model_boss_yolo(page_or_boss_name: str):
    if (page_or_boss_name in ["鸣钟之龟", "无冠者", "朔雷之鳞", "云闪之鳞", "燎照之骑", "飞廉之猩", "哀声鸷", "无常凶鹭", "辉萤军势", "聚械机偶", "无归的谬误"]
          and config.ModelName != defaultModelName):
        user_default_model()  # 1.0Boss，使用默认的yolo模型
    elif (page_or_boss_name in [ "无妄者", "无冠者之像·心脏", "角", "时序之寰",
                                 "声之领域", "异构武装", "赫卡忒", "罗蕾莱", "叹息古龙", "梦魇飞廉之猩", "梦魇无常凶鹭",
                                 "梦魇云闪之鳞", "梦魇朔雷之鳞", "梦魇无冠者", "梦魇燎照之骑", "梦魇哀声鸷",
                                 "梦魇辉萤军势", "芙露德莉斯", "梦魇凯尔匹", "荣耀狮像"]
          and config.ModelName != boss_v20):
        logger("使用[boss模型v2.0]模型")
        config.ModelName = boss_v20
        switch_model(boss_v20)


def user_default_model():
    logger(default_yolo_logger)  # 当模型文件不存在的时候，默认使用yolo模型进行识别
    config.ModelName = defaultModelName
    switch_model(defaultModelName)


# 判断模型文件是否存在
def is_in_models_folder(file_name: str):
    """
    判断给定的文件名是否在当前项目的根目录的models文件夹中。

    参数：
        file_name (str): 要检查的文件名。

    返回：
        bool: 如果文件存在于models文件夹中，则返回True，否则返回False。
    """
    models_folder = os.path.join(config.project_root, "models")  # 拼接models文件夹的完整路径
    file_path = os.path.join(models_folder, file_name)  # 拼接文件的完整路径

    return os.path.exists(file_path)  # 检查文件是否存在并返回布尔值

# 示例用法
# result = is_in_models_folder("jue.onnx")
# print(result)  # 输出 True 或 False，取决于 "example.txt" 是否存在于当前项目根目录的models文件夹中
