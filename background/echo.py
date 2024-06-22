# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: echo.py
@time: 2024/6/20 下午10:14
@author RoseRin0
"""
from pydantic import BaseModel, Field

# 定义通用属性列表
common_attributes = ["攻击", "防御", "生命"]
special_attributes_cost3 = ["共鸣效率", "冷凝伤害加成", "热熔伤害加成", "导电伤害加成", "气动伤害加成", "衍射伤害加成", "湮灭伤害加成"]
special_attributes_cost4 = ["治疗效果加成", "暴击", "暴击伤害"]


# 定义一个函数来创建字段
def create_field(attributes: list[str], title: str):
    return Field(attributes, title=title)


class EchoModel(BaseModel):
    echoSetName: list[str] = create_field(
        [
            "凝夜白霜", "熔山裂谷", "彻空冥雷", "啸谷长风", "浮星祛暗", "沉日劫明", "隐世回光", "轻云出月", "不绝余音",
        ],
        title="声骸套装名称"
    )
    echoCost: list[str] = create_field(
        [
            "1", "3", "4",
        ],
        title="声骸Cost数量"
    )
    echoCost1MainStatus: list[str] = create_field(
        common_attributes,
        title="1Cost声骸主属性",
    )
    echoCost3MainStatus: list[str] = create_field(
        common_attributes + special_attributes_cost3,
        title="3Cost声骸主属性",
    )
    echoCost4MainStatus: list[str] = create_field(
        common_attributes + special_attributes_cost4,
        title="4Cost声骸主属性",
    )


echo = EchoModel()
