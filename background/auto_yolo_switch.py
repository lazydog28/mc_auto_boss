import os
from status import logger
from config import config






   
default_yolo_logger = "使用【默认YOLO】模型进行识别" #默认模型的log日志
ModelName_ext = ".onnx" # 模型文件的后缀名

#模型文件名称
defaultModelName = "yolo"   #  默认
jue_ModelName = "jue"       #  角
heart_ModelName = "heart"  #  无冠者之像·心脏

#Boss名称
jue_bossName = "角"          #  角
jue_bossName_as = "时序之寰"
heart_bossName = "无冠者之像·心脏"  #  无冠者之像·心脏


# 作用：将模型独立分开，易于定位分析问题与维护
# 根据boss名称动态的切换模型，
def model_boss_yolo(bossName:str):
    # 没有指定使用该模型，但是该模型是存在的
    if (bossName == jue_bossName or bossName == jue_bossName_as) and config.ModelName !=jue_ModelName: # 角，并且没有切换模型,该方法的调用位于schema.py 282行
            # todo...可以判断模型是否存在，如果不存在则使用默认的模型yolo
            if is_in_models_folder(jue_ModelName+ModelName_ext):
                logger("使用【角】的YOLO模型识别")  
                config.ModelName = jue_ModelName
            else:
                user_default_model()           #  角模型不存在，使用默认的yolo模型

    elif (bossName == heart_bossName  and config.ModelName !=heart_ModelName): # 无冠者之像·心脏，并且没有切换模型,该方法的调用位于schema.py 282行
            if is_in_models_folder(heart_ModelName+ModelName_ext):
                    logger("使用【无冠者之像·心脏】的YOLO模型识别")  
                    config.ModelName = heart_ModelName
                            
            else:
                    
                user_default_model()            #  无冠者之像·心脏模型不存在，使用默认的yolo模型
           

    #  todo...待训练其他的BOSS

    # utils.py 222行调用当前方法
    elif (bossName == "鸣钟之龟" or bossName=="无冠者" or bossName=="朔雷之鳞" or bossName=="云闪之鳞" or bossName=="燎照之骑" or bossName=="飞廉之猩" or  bossName == "袁声鸷" or bossName == "无常凶鹭" or bossName == "辉萤军势" or bossName == "聚械机偶") and config.ModelName!=defaultModelName:

        user_default_model()           #  其他Boss，使用默认的yolo模型
                  



def user_default_model():
        logger(default_yolo_logger) # 当模型文件不存在的时候，默认使用yolo模型进行识别    
        config.ModelName = defaultModelName 
       

# 判断模型文件是否存在
def is_in_models_folder(file_name:str):
    """
    判断给定的文件名是否在当前项目的根目录的models文件夹中。

    参数：
        file_name (str): 要检查的文件名。

    返回：
        bool: 如果文件存在于models文件夹中，则返回True，否则返回False。
    """
    current_path = os.getcwd()  # 获取当前工作目录的路径
    models_folder = os.path.join(current_path, 'models')  # 拼接models文件夹的完整路径
    file_path = os.path.join(models_folder, file_name)  # 拼接文件的完整路径

    return os.path.exists(file_path)  # 检查文件是否存在并返回布尔值

# 示例用法
# result = is_in_models_folder("jue.onnx")
# print(result)  # 输出 True 或 False，取决于 "example.txt" 是否存在于当前项目根目录的models文件夹中