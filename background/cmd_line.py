"""
@software: PyCharm
@file: cmd_line.py
@time: 2024/6/25 下午8:00
@author wakening
"""
import os
import sys
import getopt
from pynput.keyboard import Key
from collections import OrderedDict
from constant import root_path


# 获取命令行参数，可指定配置文件的路径和启动后执行的任务
def get_cmd_opts():
    cmd_short_opts: str = "t:c:"
    cmd_long_opts: list[str] = ["task=", "config="]
    opts = sys.argv[1:]
    try:
        return getopt.getopt(opts, cmd_short_opts, cmd_long_opts)
    except getopt.GetoptError as e:
        print("\n启动参数异常: " + str(opts), e)


# 获取配置文件绝对路径，文件名优先取命令行参数-c/--config内的值
def get_config_path():
    config_file_name = "config.yaml"
    cmd_opts, cmd_args = get_cmd_opts()
    # ['E:\\mc_auto_boss\\background\\main.py', '-t', 'F5,F6', '-c', 'xxx.yaml', '--task=F5,F6', '--config=xxx.yaml']
    # print(sys.argv)
    # [('-t', 'F5,F6'), ('-c', 'xxx.yaml'), ('--task', 'F5,F6'), ('--config', 'xxx.yaml')]
    # print(cmd_opts)
    # []
    # print(cmd_args)
    for opt_left, opt_right in cmd_opts:
        if opt_left in ("-c", "--config"):
            config_file_name = opt_right
            break
    return os.path.join(root_path, config_file_name)


# 获取启动后执行的任务，命令行-t/--task参数
def get_cmd_task_opts():
    cmd_opts, cmd_args = get_cmd_opts()
    task_dict: OrderedDict[str, Key] = OrderedDict()
    cmd_tasks = None
    # [('-t', 'F5,F6'), ('-c', 'xxx.yaml'), ('--task', 'F5,F6'), ('--config', 'xxx.yaml')]
    for opt_left, opt_right in cmd_opts:
        if opt_left in ("-t", "--task"):
            cmd_tasks = opt_right.split(",")
            break
    if cmd_tasks is None or len(cmd_tasks) == 0:
        return None
    for key in cmd_tasks:
        key = key.strip().upper()
        match key:
            case "F5":
                task_dict["F5"] = Key.f5
            case "F6":
                task_dict["F6"] = Key.f6
            case "F7":
                task_dict["F7"] = Key.f7
            case "F8":
                task_dict["F8"] = Key.f8
            case "F12":
                task_dict["F12"] = Key.f12
            case "":
                pass
            case _:
                print("\n忽略不支持的任务: %s" % key)
    if (len(task_dict) > 1
            and task_dict.get("F5") is not None
            and list(task_dict.keys())[-1] != "F5"):
        print("\n自动将任务F5移至最后执行")
        task_dict.move_to_end("F5")
    # print(task_dict)
    # print(task_dict.keys())
    # print(sys.argv)
    return task_dict
