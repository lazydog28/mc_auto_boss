# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: config.py
@time: 2024/6/1 下午9:13
@author SuperLazyDog
"""
from pydantic import BaseModel, Field, ValidationError, validator
import yaml
import os
import winreg
import sys
from typing import Optional, Dict, List


class Config(BaseModel):
    MaxFightTime: int = Field(120, title="最大战斗时间")
    MaxIdleTime: int = Field(10, title="最大空闲时间", ge=5)
    MaxEchoAbsorptionTime: int = Field(10, title="最大空闲时间", ge=5)
    ReloadPagesAndConditional: bool = Field(False, title="是否动态加载页面和条件")
    TargetBoss: list[str] = Field([], title="目标关键字")
    SelectRoleInterval: int = Field(2, title="选择角色间隔时间", ge=2)
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
    FightTacticsConcerto: list[str] = Field(
        [
            "",
            "",
            "",
        ],
        title="变奏入场时的技能释放顺序",
    )

    DungeonWeeklyBossLevel: int = Field(40, title="周本(副本)boss等级")
    EchoSearchModelChange: bool = Field(True, title="是否启用声骸模型切换")
    SearchEchoes: bool = Field(False, title="是否搜索声骸")
    OcrInterval: float = Field(0.5, title="OCR间隔时间", ge=0)
    SearchDreamlessEchoes: bool = Field(True, title="是否搜索无妄者")
    CharacterHeal: bool = Field(True, title="是否判断角色是否阵亡")
    WaitUltAnimation: bool = Field(False, title="是否等待大招时间")
    EchoLock: bool = Field(False, title="是否启用锁定声骸功能")
    EchoLockConfig: Dict[str, Dict[str, List[str]]] = Field(default_factory=dict)
    EchoMaxContinuousLockQuantity: int = Field(5, title="最大连续检测到已锁定声骸的数量")
    GameMonitorTime: int = Field(5, title="游戏窗口检测间隔时间")
    EchoDebugMode: bool = Field(True, title="声骸锁定功能DEBUG显示输出的开关")
    EchoSynthesisDebugMode: bool = Field(True, title="声骸合成锁定功能DEBUG显示输出的开关")
    UseConsumables: bool = Field(False, title="是否使用消耗品")
    ConsumablesName: str = Field(None, title="使用的料理或药水名称")
    UseSpecialCode: bool = Field(False, title="是否使用分boss的进图前的特殊代码")
    RebootCount: int = Field(0, title="截取窗口失败次数")
    GameResolution: List = Field(None, title="游戏分辨率")
    # 获取项目根目录
    project_root: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    user_data_root: str = os.path.join(project_root, "user_data")
    LogFilePath: Optional[str] = Field(None, title="日志文件路径")

    AppPath: Optional[str] = Field(None, title="游戏路径")

    def __init__(self, **data):
        super().__init__(**data)
        if not self.LogFilePath:
            self.LogFilePath = os.path.join(self.project_root, "mc_log.txt")
        if not self.AppPath:
            self.AppPath = get_wuthering_waves_path()


# 获取鸣潮游戏路径
def get_wuthering_waves_path():
    key = None
    try:
        # 打开注册表项
        key_path = r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\KRInstall Wuthering Waves"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)

        try:
            # 读取安装路径
            install_path, _ = winreg.QueryValueEx(key, "InstallPath")
            if install_path:
                # 构造完整的程序路径
                program_path = os.path.join(install_path, "Wuthering Waves Game", "Wuthering Waves.exe")
                # print(f"从注册表中加载到游戏目录：{program_path}")
                return program_path
        except FileNotFoundError:
            # print("无法在注册表中找到游戏路径.")
            pass
    except Exception as e:
        # print(f"访问注册表错误: {e}")
        pass
    finally:
        try:
            if 'key' in locals():
                key.Close()
        except Exception:
            print(f"未在注册表找到鸣潮游戏路径，请在Config第一行手动设置")
            wait_exit()
    return None


def wait_exit():
    input("按任意键退出...")
    sys.exit(0)


root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


project_root = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(project_root, "config.yaml")

# 判断是否存在配置文件
if os.path.exists(os.path.join(root_path, "config.yaml")):
    with open(os.path.join(root_path, "config.yaml"), "r", encoding="utf-8") as f:
        try:
            print("加载配置文件中")
            config = Config(**yaml.safe_load(f))
        except yaml.YAMLError as e:
            if hasattr(e, 'problem_mark'):
                mark = e.problem_mark
                print(f"配置文件有误，请检查config.yaml，错误位于【第{mark.line + 1}行】【第{mark.column + 1}列】，或其上下行符号错误。")
                print("常见问题:\n① 冒号(:)后需要空格，否则会导致缩进错误。\n② 列表中存在逗号错误('，'和',')等\n③ 请全部使用半角字符，请仔细检查")
                wait_exit()
            else:
                print(f"配置文件格式有误，请检查config.yaml: {e}")
        except ValidationError as e:
            errors = e.errors()
            for error in errors:
                if 'FightTacticsConcerto' in error['loc']:
                    print("变奏入场连招设置有误，请检查config.yaml中的FightTacticsConcerto列表")
                    break
            else:
                print(f"配置文件格式有误，请检查config.yaml: {e}")
            wait_exit()
else:
    print("缺少配置文件，请复制config.example.yaml并重命名为config.yaml进行修改")
    wait_exit()

if len(config.TargetBoss) == 0:
    print("请在项目根目录下的config.yaml中填写目标BOSS全名")
    wait_exit()

# 加载声骸锁定配置文件
if config.EchoLock:
    if os.path.exists(os.path.join(root_path, "echo_config.yaml")):
        with open(os.path.join(root_path, "echo_config.yaml"), "r", encoding="utf-8") as f:
            try:
                echo_config_data = yaml.safe_load(f)
                config.EchoLockConfig = echo_config_data.get("EchoLockConfig", {})
            except yaml.YAMLError as e:
                if hasattr(e, 'problem_mark'):
                    mark = e.problem_mark
                    print(f"配置文件有误，请检查echo_config.yaml，错误位于【第{mark.line + 1}行】【第{mark.column + 1}列】，或其上下行符号错误。")
                    print("常见问题:\n① 冒号(:)后需要空格，否则会导致缩进错误。\n② 列表中存在逗号错误('，'和',')等\n③ 请全部使用半角字符，请仔细检查")
                    wait_exit()
                else:
                    print(e)
                    print(f"声骸配置文件有误，请检查echo_config.yaml：{e}")
                    wait_exit()
    else:
        print("缺少声骸配置文件，请复制echo_config.example.yaml并重命名为请复制echo_config.yaml进行修改")
        wait_exit()
