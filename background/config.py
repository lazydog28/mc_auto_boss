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


class Config(BaseModel):
    MaxBossTime: int = Field(120, title="最大战斗时间")
    MaxNoBossTime: int = Field(240, title="最大非战斗时间")


# 判断是否存在配置文件
if os.path.exists("config.yaml"):
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = Config(**yaml.safe_load(f))
else:
    config = Config()
    with open("config.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(config.dict(), f)
