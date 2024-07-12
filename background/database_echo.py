# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: database_echo.py
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
    echoName: list[str] = create_field(
        [
            "呼咻咻", "咔嚓嚓", "阿嗞嗞", "呜咔咔", "叮咚咚", "咕咕河豚", "啾啾河豚", "遁地鼠", "绿熔蜥稚形", "碎獠猪", "火鬃狼",
            "晶螯蝎", "游弋蝶", "寒霜陆龟", "幼猿", "融火虫", "侏侏鸵", "青羽鹭", "紫羽鹭", "绿熔蜥", "箭簇熊", "暗鬃狼", "戏猿",
            "雪鬃狼", "踏光兽", "飞廉之猩", "无常凶鹭", "哀声鸷", "无冠者", "无妄者", "鸣钟之龟", "冷凝棱镜", "热熔棱镜",
            "湮灭棱镜", "衍射棱镜", "辉萤军势", "车刃镰", "聚械机偶", "刺玫菇稚形", "先锋幼岩", "裂变幼岩", "刺玫菇", "坚岩斗士",
            "惊蛰猎手", "破霜猎手", "巡徊猎手", "鸣泣战士", "审判战士", "振铎乐师", "奏谕乐师", "冥渊守卫", "磐石守卫", "朔雷之鳞",
            "云闪之鳞", "燎照之骑", "通行灯偶", "巡哨机傀", "游鳞机枢", "角"
        ],
        title="声骸名称"
    )
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
