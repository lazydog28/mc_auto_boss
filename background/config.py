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
from constant import wait_exit


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
        title="战斗策略, 逗号分隔, e,q,r为技能, a为普攻, 数字为间隔时间,a~0.5为普工按下0.5秒",
    )
    DreamlessLevel: int = Field(40, title="无妄者推荐等级")
    SearchEchoes: bool = Field(False, title="是否搜索回音")


# 判断是否存在配置文件
if os.path.exists("config.yaml"):
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = Config(**yaml.safe_load(f))
else:
    config = Config()
    with open("config.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(config.dict(), f)

if len(config.TargetBoss) == 0:
    print("请在config.yaml中填写目标BOSS全名")
    wait_exit()
