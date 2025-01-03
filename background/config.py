# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: config.py
@time: 2024/6/1 下午9:13
@author SuperLazyDog
"""
from pydantic import BaseModel, Field
import yaml
import shutil
import os
import winreg
from cmd_line import get_config_path
from constant import wait_exit, root_path
from typing import Optional, Dict, List
from echo import EchoModel


class Config(BaseModel):
    # 脚本基础配置
    AppPath: Optional[str] = Field(None, title="游戏路径")
    ModelName: Optional[str] = Field("yolo", title="模型的名称,默认是yolo.onnx")
    OcrInterval: float = Field(0.5, title="OCR间隔时间", ge=0)
    GameMonitorTime: int = Field(5, title="游戏窗口检测间隔时间")
    project_root: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LogFilePath: Optional[str] = Field(None, title="日志文件路径")

    # 游戏崩溃捕获及处理
    RestartWutheringWaves: bool = Field(
        False, title="定时重启游戏以避免游戏卡10%、75%等特殊进度"
    )
    RestartWutheringWavesTime: int = Field(7200, title="游戏自动重启间隔时间")
    RebootCount: int = Field(0, title="截取窗口失败次数")
    DetectionUE4: bool = Field(True, title="是否检测UE4崩溃")

    # 控制台信息
    EchoDebugMode: bool = Field(True, title="声骸锁定功能DEBUG显示输出的开关")
    EchoSynthesisDebugMode: bool = Field(
        True, title="声骸合成锁定功能DEBUG显示输出的开关"
    )

    # 自动战斗及声骸锁定配置
    MaxFightTime: int = Field(120, title="最大战斗时间")
    MaxIdleTime: int = Field(10, title="最大空闲时间", ge=5)
    MaxSearchEchoesTime: int = Field(18, title="最大搜索声骸时间")
    SelectRoleInterval: int = Field(2, title="选择角色间隔时间", ge=2)
    DungeonWeeklyBossLevel: int = Field(40, title="周本(副本)boss等级")
    BossWaitTime_Dreamless: float = Field(3, title="进入-无妄者-周本等待时间")
    BossWaitTime_Jue: float = Field(2, title="进入-角-周本等待时间")
    BossWaitTime_fallacy: float = Field(5, title="进入-无归的谬误-等待时间")
    BossWaitTime_sentry_construct: float = Field(8, title="进入-异构武装-等待时间")
    SearchEchoes: bool = Field(False, title="是否搜索声骸")
    SearchDreamlessEchoes: bool = Field(True, title="是否搜索无妄者")
    CharacterHeal: bool = Field(True, title="是否判断角色是否阵亡")
    WaitUltAnimation: bool = Field(False, title="是否等待大招时间")
    EchoLock: bool = Field(False, title="是否启用锁定声骸功能")
    EchoLockConfig: Dict[str, Dict[str, List[str]]] = Field(default_factory=dict)
    EchoMaxContinuousLockQuantity: int = Field(
        5, title="最大连续检测到已锁定声骸的数量"
    )

    # 战斗策略
    TargetBoss: list[str] = Field([], title="目标关键字")
    FightTactics: list[str] = Field(
        [
            "e,q,r,a,0.1,a,0.1,a,0.1,a,0.1,a,0.1",
            "e,q,r,a~0.5,0.1,a,0.1,a,0.1,a,0.1,a,0.1",
            "e~0.5,q,r,a,0.1,a,0.1,a,0.1,a,0.1,a,0.1",
        ],
        title="战斗策略 三个角色的释放技能顺序, 逗号分隔, e,q,r为技能, a为普攻(默认连点0.3秒), 数字为间隔时间,a~0.5为普攻按下0.5秒,a(0.5)为连续普攻0.5秒",
    )
    FightTacticsUlt: list[str] = Field(
        [
            "a(1.6),e,a(1.6),e,a(1.6)",
            "a(1.6),e,a(1.6),e,a(1.6)",
            "a(1.2),e",
        ],
        title="大招释放成功时的技能释放顺序",
    )
    FightOrder: list[int] = Field([1, 2, 3],
                                  title="战斗顺序，123为角色在编队和战斗策略中的位置，调整可使维里奈在编队3号位也可以先连招")

    def __init__(self, **data):
        super().__init__(**data)
        if not self.LogFilePath:
            self.LogFilePath = os.path.join(self.project_root, "mc_log.txt")
        if not self.AppPath:
            self.AppPath = get_wuthering_waves_path()


# 获取鸣潮游戏路径
def open_registry_key(key_path):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        return key
    except FileNotFoundError:
        # print(f"未找到注册表路径'{key_path}'")
        pass
    except Exception as e:
        print(f"访问注册表错误: {e}")
    return None


def get_wuthering_waves_path():
    key = None
    # 打开注册表项
    # key_path = r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\KRInstall Wuthering Waves"

    key_paths = [
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\KRInstall Wuthering Waves",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\KRInstall Wuthering Waves Overseas",
    ]

    for key_path in key_paths:
        key = open_registry_key(key_path)

        if key:
            try:
                # 读取安装路径
                install_path, _ = winreg.QueryValueEx(key, "InstallPath")
                if install_path:
                    # 构造完整的程序路径
                    program_path = os.path.join(
                        install_path, "Wuthering Waves Game", "Wuthering Waves.exe"
                    )
                    # print(f"从注册表中加载到游戏目录：{program_path}")
                    return program_path
            except Exception as e:
                # print(f"构建安装路径错误: {e}")
                pass
            finally:
                if "key" in locals():
                    key.Close()

    return None


config_path = get_config_path()
# 判断是否存在配置文件
if os.path.exists(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        config = Config(**yaml.safe_load(f))
else:
    config = Config()
    # with open(config_path, "w", encoding="utf-8") as f:
    #     yaml.safe_dump(config.dict(), f)
    """
    若初始化时config文件不存在将复制example自动生成config文件
    替代之版本yaml函数读取无注释字符串流版本的无格式config文件
    并提醒用户配置文件
    """
    config_example = os.path.join(config.project_root, "config.example.yaml")
    config_auto = os.path.join(config.project_root, "config.yaml")
    with open(config_example, "rb") as source_file:
        with open(config_auto, "wb") as dest_file:
            shutil.copyfileobj(source_file, dest_file)
    print("\n未找到配置文件，已按example为模板自动生成，请进行配置")

if len(config.TargetBoss) == 0:
    print("请在配置文件中填写目标BOSS全名，配置文件路径: %s" % config_path)
    wait_exit()

# 加载声骸锁定配置文件
if config.EchoLock:
    echo_config_path = os.path.join(root_path, "echo_config.yaml")
    if os.path.exists(echo_config_path):
        with open(
            echo_config_path, "r", encoding="utf-8"
        ) as f:
            echo_config_data = yaml.safe_load(f)
            config.EchoLockConfig = echo_config_data.get("EchoLockConfig", {})
        # 补齐数据结构，保证该有的key和value都有，将没有的值赋为空数组而非None，
        # 保证后续遍历处理时每个套装都能过一遍，也不用再判None
        echo_model = EchoModel()
        for echo_set_name in echo_model.echoSetName:
            if config.EchoLockConfig is None:
                config.EchoLockConfig = {}
            echo_set_dict = config.EchoLockConfig.get(echo_set_name)
            if echo_set_dict is None:
                echo_set_dict = {}
                for cost in echo_model.echoCost:
                    echo_set_dict[cost + "COST"] = []
            for cost in echo_model.echoCost:
                if not echo_set_dict.get(cost + "COST_ECHO"):
                    echo_set_dict[cost + "COST_ECHO"] = {}
            config.EchoLockConfig[echo_set_name] = echo_set_dict
        # print("\n" + str(config.EchoLockConfig))
    else:
        print("缺少声骸配置文件，请复制example文件进行配置，目标文件路径：%s" % echo_config_path)
        wait_exit()
