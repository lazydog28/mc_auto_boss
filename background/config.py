# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: config.py
@time: 2024/6/1 下午9:13
@author SuperLazyDog
"""
from pydantic import BaseModel, Field
import yaml
import os
import winreg
from constant import wait_exit, root_path
from typing import Optional, Dict, List


class Config(BaseModel):
    MaxFightTime: int = Field(120, title="最大战斗时间")
    MaxIdleTime: int = Field(10, title="最大空闲时间", ge=5)
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
    DreamlessWaitTime: int = Field(5, title="无妄者等待时间", ge=0)
    SearchEchoes: bool = Field(False, title="是否搜索声骸")
    OcrInterval: float = Field(0.5, title="OCR间隔时间", ge=0)
    SearchDreamlessEchoes: bool = Field(True, title="是否搜索无妄者")
    CharacterHeal: bool = Field(True, title="是否判断角色是否阵亡")
    WaitUltAnimation: bool = Field(False, title="是否等待大招时间")
    EchoLock: bool = Field(False, title="是否启用锁定声骸功能")
    EchoLockConfig: Dict[str, Dict[str, List[str]]] = Field(default_factory=dict)
    EchoMaxContinuousLockQuantity: int = Field(5, title="最大连续检测到已锁定声骸的数量")

    # 获取项目根目录
    project_root: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_file_path: Optional[str] = Field(None, title="日志文件路径")

    AppPath: Optional[str] = Field(None, title="游戏路径")

    def __init__(self, **data):
        super().__init__(**data)
        if not self.log_file_path:
            self.log_file_path = os.path.join(self.project_root, "mc_log.txt")
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
        if 'key' in locals():
            key.Close()
    return None


project_root = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(project_root, "config.yaml")

# 判断是否存在配置文件
if os.path.exists(os.path.join(root_path, "config.yaml")):
    with open(os.path.join(root_path, "config.yaml"), "r", encoding="utf-8") as f:
        config = Config(**yaml.safe_load(f))
else:
    config = Config()
    with open(os.path.join(root_path, "config.yaml"), "w", encoding="utf-8") as f:
        yaml.safe_dump(config.dict(), f)

if len(config.TargetBoss) == 0:
    print("请在项目根目录下的config.yaml中填写目标BOSS全名")
    wait_exit()

# 加载声骸锁定配置文件
if config.EchoLock:
    if os.path.exists(os.path.join(root_path, "echo_config.yaml")):
        with open(os.path.join(root_path, "echo_config.yaml"), "r", encoding="utf-8") as f:
            echo_config_data = yaml.safe_load(f)
            config.EchoLockConfig = echo_config_data.get("EchoLockConfig", {})
    else:
        print("缺少声骸配置文件")
        wait_exit()
