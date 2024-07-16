# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: database_echo.py
@time: 2024/7/9 上午9:46
@author RoseRin0
"""
import os
import re
from config import root_path
from status import info, logger

image_file_path = os.path.join(root_path, "template/")


class ItemDatabase:
    def __init__(self):
        self.foods = []
        self.potions = []

    def add_food(self, item_id, item_name, item_effect, item_duration, item_image_filename):
        food = {
            "item_id": item_id,
            "item_name": item_name,
            "item_effect": item_effect,
            "item_duration": item_duration,
            "image_filename": os.path.join(image_file_path, "food/" + item_image_filename + ".png")
        }
        self.foods.append(food)

    def add_potion(self, item_id, item_name, item_effect, item_duration, item_image_filename):
        potion = {
            "item_id": item_id,
            "item_name": item_name,
            "item_effect": item_effect,
            "item_duration": item_duration,
            "image_filename": os.path.join(image_file_path, "potion/" + item_image_filename + ".png")
        }
        self.potions.append(potion)

    def get_all_foods(self):
        return self.foods

    def get_all_potions(self):
        return self.potions

    # 获取消耗品功能种类
    def get_consumables_effect_type(self, item_name):
        keywords = {
            r'提高.*抗性': '抗性提升',
            r'提高.*伤害加成': '伤害加成',
            r'回复生命': '生命恢复',
            r'恢复意识': '意识恢复',
            r'提高.*攻击力': '攻击力提升',
            r'提高.*暴击率': '暴击率提升',
            r'提高.*防御力': '防御力提升',
            r'提高.*生命上限': '生命上限提升',
            r'声骸吸收.*提升': '声骸吸收概率提升'
        }
        for item in self.foods + self.potions:
            if item["item_name"] == item_name:
                for pattern, effect_type in keywords.items():
                    if re.search(pattern, item["item_effect"]):
                        return effect_type
                return "其他功能"
        return "其他功能"

    # 获取消耗品ID
    def get_consumables_id(self, item_name):
        for item in self.foods + self.potions:
            if item["item_name"] == item_name:
                return item["item_id"]

    # 获取消耗品效果描述
    def get_consumables_effect(self, item_name):
        for item in self.foods + self.potions:
            if item["item_name"] == item_name:
                return item["item_effect"]

    # 获取消耗品持续时间
    def get_consumables_duration(self, item_name):
        for item in self.foods + self.potions:
            if item["item_name"] == item_name:
                return item["item_duration"]

    # 获取消耗品图片路径
    def get_consumables_image_path(self, item_name):
        for item in self.foods + self.potions:
            if item["item_name"] == item_name:
                return item["image_filename"]

    # 获取消耗品信息
    def get_consumables_info(self, item_name):
        consumables_info = []
        for item in self.foods + self.potions:
            if item["item_name"] == item_name:
                consumables_info.append(self.get_consumables_id(item_name))
                consumables_info.append(item_name)
                consumables_info.append(self.get_consumables_effect_type(item_name))
                consumables_info.append(self.get_consumables_effect(item_name))
                consumables_info.append(self.get_consumables_duration(item_name))
                consumables_info.append(self.get_consumables_image_path(item_name))
                logger(
                    f"获取消耗品信息成功\n"
                    f"消耗品名称：{consumables_info[1]}\n"
                    f"消耗品类别：{consumables_info[2]}\n"
                    f"消耗品描述：{consumables_info[3]}\n"
                    f"持续时间：{consumables_info[4]}秒", "DEBUG"
                )
                return consumables_info

        logger(f"获取{item_name}信息失败，未找到该消耗品", "DEBUG")
        return False


# 初始化数据库
db = ItemDatabase()

# 食物
db.add_potion(
    "42100001",
    "热熔防护喷雾",
    "提高队伍中所有共鸣者15%热熔伤害抗性，持续时间180秒，在多人游戏中仅对自己的角色生效。",
    180,
    "Fusion_Resistance_Spray"
)
db.add_potion(
    "42100002",
    "气动防护喷雾",
    "提高队伍中所有共鸣者15%气动伤害抗性，持续时间180秒，在多人游戏中仅对自己的角色生效。",
    180,
    "Aero_Resistance_Spray"
)
db.add_potion(
    "42100003",
    "导电防护喷雾",
    "提高队伍中所有共鸣者15%导电伤害抗性，持续时间180秒，在多人游戏中仅对自己的角色生效。",
    180,
    "Electro_Resistance_Spray"
)
db.add_potion(
    "42100004",
    "冷凝防护喷雾",
    "提高队伍中所有共鸣者15%冷凝伤害抗性，持续时间180秒，在多人游戏中仅对自己的角色生效。",
    180,
    "Glacio_Resistance_Spray"
)
db.add_potion(
    "42100005",
    "衍射防护喷雾",
    "提高队伍中所有共鸣者15%衍射伤害抗性，持续时间180秒，在多人游戏中仅对自己的角色生效。",
    180,
    "Spectro_Resistance_Spray"
)
db.add_potion(
    "42100006",
    "湮灭防护喷雾",
    "提高队伍中所有共鸣者15%湮灭伤害抗性，持续时间180秒，在多人游戏中仅对自己的角色生效。",
    180,
    "Havoc_Resistance_Spray"
)
db.add_potion(
    "42100007",
    "热熔双联合剂",
    "提高队伍中所有共鸣者15%热熔伤害加成，持续时间180秒，在多人游戏中仅对自己的角色生效。",
    180,
    "Fusion_Petrol"
)
db.add_potion(
    "42100008",
    "气动双联合剂",
    "提高队伍中所有共鸣者15%气动伤害加成，持续时间180秒，在多人游戏中仅对自己的角色生效。",
    180,
    "Aero_Petrol"
)
db.add_potion(
    "42100009",
    "导电双联合剂",
    "提高队伍中所有共鸣者15%导电伤害加成，持续时间180秒，在多人游戏中仅对自己的角色生效。",
    180,
    "Electro_Petrol"
)
db.add_potion(
    "42100010",
    "冷凝双联合剂",
    "提高队伍中所有共鸣者15%冷凝伤害加成，持续时间180秒，在多人游戏中仅对自己的角色生效。",
    180,
    "Glacio_Petrol"
)
db.add_potion(
    "42100011",
    "衍射双联合剂",
    "提高队伍中所有共鸣者15%衍射伤害加成，持续时间180秒，在多人游戏中仅对自己的角色生效。",
    180,
    "Spectro_Petrol"
)
db.add_potion(
    "42100012",
    "湮灭双联合剂",
    "提高队伍中所有共鸣者15%湮灭伤害加成，持续时间180秒，在多人游戏中仅对自己的角色生效。",
    180,
    "Havoc_Petrol"
)
db.add_potion(
    "42100013",
    "初级复苏吸雾",
    "可使队伍中指定共鸣者即时恢复意识并回复100点生命值，每60秒只能使用一次（多人游戏中只对自己的角色生效）。",
    0,
    "Basic_Revival_Inhaler"
)
db.add_potion(
    "42100014",
    "中级复苏吸雾",
    "可使队伍中指定共鸣者即时恢复意识并回复10%生命上限，每60秒只能使用一次（多人游戏中只对自己的角色生效）。",
    0,
    "Medium_Revival_Inhaler"
)
db.add_potion(
    "42100015",
    "高级复苏吸雾",
    "可使队伍中指定共鸣者即时恢复意识并回复25%生命上限，每60秒只能使用一次（多人游戏中只对自己的角色生效）。",
    0,
    "Advanced_Revival_Inhaler"
)
db.add_potion(
    "42100016",
    "特级复苏吸雾",
    "可使队伍中指定共鸣者即时恢复意识并回复完全恢复生命，每60秒只能使用一次（多人游戏中只对自己的角色生效）。",
    0,
    "Premium_Revival_Inhaler"
)
db.add_potion(
    "42100017",
    "初级营养块",
    "可使队伍中指定共鸣者回复生命上限10%的生命值和500点固定生命值（多人游戏中只对自己的角色生效）。",
    0,
    "Basic_Nutrient_Block"
)
db.add_potion(
    "42100018",
    "中级营养块",
    "可使队伍中指定共鸣者回复生命上限15%的生命值和1000点固定生命值（多人游戏中只对自己的角色生效）。",
    0,
    "Medium_Nutrient_Block"
)
db.add_potion(
    "42100019",
    "高级营养块",
    "可使队伍中指定共鸣者回复生命上限20%的生命值和1500点固定生命值（多人游戏中只对自己的角色生效）。",
    0,
    "Advanced_Nutrient_Block"
)
db.add_potion(
    "42100020",
    "活力饮料",
    "饮用后为当前共鸣者回复生命上限20%的生命值和160点固定生命值。",
    0,
    "Vitality_Drink"
)
db.add_potion(
    "42100021",
    "特级营养块",
    "可使队伍中指定共鸣者回复生命上限30%的生命值和2000点固定生命值（多人游戏中只对自己的角色生效）。",
    0,
    "Premium_Nutrient_Block"
)
db.add_potion(
    "42100022",
    "初级能量袋",
    "可使队伍中指定共鸣者每秒回复生命100点固定生命值，持续30秒（多人游戏中只对自己的角色生效）。",
    30,
    "Basic_Energy_Bag"
)
db.add_potion(
    "42100023",
    "中级能量袋",
    "可使队伍中指定共鸣者每秒回复生命150点固定生命值，持续30秒（多人游戏中只对自己的角色生效）。",
    30,
    "Medium_Energy_Bag"
)
db.add_potion(
    "42100024",
    "高级能量袋",
    "可使队伍中指定共鸣者每秒回复生命上限2%的生命值和200点固定生命值，持续30秒（多人游戏中只对自己的角色生效）。",
    30,
    "Advanced_Energy_Bag"
)
db.add_potion(
    "42100025",
    "特级能量袋",
    "可使队伍中指定共鸣者每秒回复生命上限3%的生命值和300点固定生命值，持续30秒（多人游戏中只对自己的角色生效）。",
    30,
    "Premium_Energy_Bag"
)
db.add_potion(
    "42100026",
    "超音速溶剂",
    "可使队伍中指定共鸣者的声骸技能冷却时间缩短30%，持续时间180秒，在多人游戏中仅对自己的角色生效。",
    180,
    "Supersonic_Solvent"
)
db.add_potion(
    "42100027",
    "训练师溶剂",
    "可使队伍中所有共鸣者释放的声骸技能伤害提升40%，持续时间180秒，在多人游戏中仅对自己的角色生效。",
    180,
    "Trainer_Solvent"
)
db.add_potion(
    "42100028",
    "弦乐溶剂",
    "可使队伍中指定共鸣者每秒回复1点协奏值，持续时间180秒，在多人游戏中仅对自己的角色生效。",
    180,
    "String_Solvent"
)
db.add_potion(
    "42100029",
    "鼓手溶剂",
    "可使队伍中所有共鸣者的共鸣效率提升30%，持续时间180秒，在多人游戏中仅对自己的角色生效。",
    180,
    "Drummer_Solvent"
)
db.add_potion(
    "42100030",
    "单体复苏剂",
    "使用该物品后可使编队内的指定共鸣者即时恢复意识，且每60秒只能使用一次（多人游戏中只对自己的角色生效）。",
    60,
    "Single_Revival_Agent"
)
db.add_potion(
    "42100031",
    "五号效果药剂",
    "饮用后为当前共鸣者回复生命上限20%的生命值和160点固定生命值。",
    0,
    "Potion_No._5"
)
db.add_potion(
    "42100032",
    "撞金合剂",
    "可使队伍中指定共鸣者触发逆势回击时，额外削减敌人一定比例的共振度，持续时间60秒，在多人游戏中仅对自己的角色生效。",
    60,
    "Morale_Tablets"
)
db.add_potion(
    "42100033",
    "划音合剂",
    "可使队伍中指定共鸣者释放变奏技能后，回复20点协奏能量，持续时间60秒，在多人游戏中仅对自己的角色生效。",
    60,
    "Harmony_Tablets"
)
db.add_potion(
    "42100034",
    "激声合剂",
    "可使队伍中指定共鸣者成功闪避时，回复5点共鸣能量，持续时间60秒，在多人游戏中仅对自己的角色生效。",
    60,
    "Passion_Tablets"
)
db.add_potion(
    "42100035",
    "强心合剂",
    "可使队伍中指定共鸣者在首次受到致命伤害时免疫该次伤害，并回复生命上限25%的生命值，持续时间60秒，在多人游戏中仅对自己的角色生效。",
    60,
    "Vigor_Tablets"
)

# 料理
db.add_food(
    "80000000",
    "今州烤串",
    "提高队伍中所有共鸣者100点攻击力，持续时间15分钟，在多人游戏中仅对自己的角色生效。",
    900,
    "Jinzhou_Skewers"
)
db.add_food(
    "80000001",
    "锅盔",
    "提高队伍中所有共鸣者200点防御力，持续时间15分钟，在多人游戏中仅对自己的角色生效。",
    900,
    "Helmet_Flatbread"
)
db.add_food(
    "80000002",
    "凉拌香苏",
    "提高队伍中所有共鸣者10%暴击率，持续时间15分钟，在多人游戏中仅对自己的角色生效。",
    900,
    "Perilla_Salad"
)
db.add_food(
    "80000003",
    "红油手撕鸡",
    "减少队伍中所有共鸣者15%纵跑、游泳耐力消耗，持续时间15分钟，在多人游戏中仅对自己的角色生效。",
    900,
    "Spicy_Pulled_Chicken"
)
db.add_food(
    "80000004",
    "龙须酥",
    "恢复80点耐力。",
    0,
    "Loong_Whiskers_Crisp"
)
db.add_food(
    "80000005",
    "戍边粮",
    "减少队伍中指定共鸣者25%钩索冷却时间，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Food_Ration_Bar"
)
db.add_food(
    "80000006",
    "每日清茶",
    "提高队伍中所有共鸣者800点生命上限，持续时间15分钟，在多人游戏中仅对自己的角色生效。",
    900,
    "Refreshment_Tea"
)
db.add_food(
    "80000007",
    "咸奶茶",
    "在野外击败敌人时获得的贝币增加25%，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Salted_Milk_Tea"
)
db.add_food(
    "80000008",
    "清芬茶",
    "提高队伍中所有共鸣者25%生命上限，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Angelica_Tea"
)
db.add_food(
    "80000009",
    "舒云秘制凉茶",
    "提高队伍中所有共鸣者12%攻击力和10%暴击率，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Shuyun_Herbal_Tea"
)
db.add_food(
    "80000010",
    "香汁鸡",
    "减少队伍中指定共鸣者15%钩索冷却时间，持续时间15分钟，在多人游戏中仅对自己的角色生效。",
    900,
    "Poached_Chicken"
)
db.add_food(
    "80000011",
    "辛香肉片",
    "提高队伍中所有共鸣者25%攻击力，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Spicy_Meat_Slices"
)
db.add_food(
    "80000012",
    "小龙包",
    "提高队伍中所有共鸣者25%防御力，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Loong_Buns"
)
db.add_food(
    "80000013",
    "铁铲花蕈",
    "提高队伍中所有共鸣者16%暴击率，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Iron_Shovel_Edodes"
)
db.add_food(
    "80000014",
    "今州烩",
    "提高队伍中所有共鸣者8%攻击力和6%暴击率，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Jinzhou_Stew"
)
db.add_food(
    "80000015",
    "拔丝菱果",
    "提高队伍中所有共鸣者18%防御力和15%生命上限，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Candied_Caltrops"
)
db.add_food(
    "80000016",
    "潮饼",
    "提高队伍中所有共鸣者30%攻击力，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Wuthercake"
)
db.add_food(
    "80000017",
    "碎金饭",
    "减少队伍中所有共鸣者20%纵跑、游泳耐力消耗，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Aureate_Fried_Rice"
)
db.add_food(
    "80000018",
    "香柠炖肉",
    "声骸吸收概率提升20%，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Lemon-Braised_Pork"
)
db.add_food(
    "80000019",
    "清芬鱼汤",
    "恢复40点耐力。",
    0,
    "Milky_Fish_Soup"
)
db.add_food(
    "80000020",
    "清葛粥",
    "提高队伍中所有共鸣者22%暴击率，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Kudzu_Congee"
)
db.add_food(
    "80000021",
    "星星酥",
    "提高队伍中所有共鸣者35%防御力，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Star_Flakes"
)
db.add_food(
    "80000022",
    "菱果炒盐雀",
    "在野外击败敌人时获得的素材增加25%，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Caltrop_Stir_Fry"
)
db.add_food(
    "80000023",
    "冬云菱果粥",
    "提高队伍中所有共鸣者30%生命上限，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Caltrop_Soup"
)
db.add_food(
    "80000024",
    "脆皮烧鸽",
    "提高队伍中所有共鸣者50%防御力，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Crispy_Squab"
)
db.add_food(
    "80000025",
    "今州冒菜",
    "提高队伍中所有共鸣者28%暴击率，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Jinzhou_Maocai"
)
db.add_food(
    "80000026",
    "龙抬头",
    "提高队伍中所有共鸣者40%生命上限，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Rising_Loong"
)
db.add_food(
    "80000027",
    "糖醋里脊",
    "声骸吸收概率提升50%，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Sweet_&_Sour_Pork"
)
db.add_food(
    "80000028",
    "油辣豆腐",
    "在野外击败敌人时获得的贝币增加50%，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Chili_Sauce_Tofu"
)
db.add_food(
    "80000029",
    "森栖锅",
    "提高队伍中所有共鸣者40%攻击力，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Morri_Pot"
)
db.add_food(
    "80000030",
    "酿肉豆腐",
    "在野外击败敌人时获得的素材增加50%，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Stuffed_Tofu"
)
db.add_food(
    "80000031",
    "失败的菜肴",
    "提高队伍中所有共鸣者50点攻击力，持续时间15分钟，在多人游戏中仅对自己的角色生效。",
    900,
    "Failed_Attempt"
)
db.add_food(
    "80000032",
    "喜凌茶",
    "提高队伍中所有共鸣者12%防御力和10%生命上限，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Happiness_Tea"
)
db.add_food(
    "80000033",
    "雪莲酥",
    "提高队伍中所有共鸣者32%暴击伤害，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Lotus_Pastry"
)
db.add_food(
    "80000034",
    "雀翎辣肉",
    "提高队伍中所有共鸣者20%共鸣效率，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Spicy_Meat_with_Pavo_Plums"
)
db.add_food(
    "80001000",
    "观剧搭档",
    "提高队伍中所有共鸣者120点攻击力，持续时间15分钟，在多人游戏中仅对自己的角色生效。",
    900,
    "Liondance_Companion"
)
db.add_food(
    "80001002",
    "冰镇香苏",
    "提高队伍中所有共鸣者12%暴击率，持续时间15分钟，在多人游戏中仅对自己的角色生效。",
    900,
    "Iced_Perilla"
)
db.add_food(
    "80001004",
    "云顶龙须酥",
    "恢复100点耐力。",
    0,
    "Silky_Reveries"
)
db.add_food(
    "80001005",
    "能量饼干",
    "减少队伍中指定共鸣者30%钩索冷却时间，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Ration_Bar"
)
db.add_food(
    "80001008",
    "三清茶",
    "提高队伍中所有共鸣者28%生命上限，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Sanqing_Tea"
)
db.add_food(
    "80001012",
    "剔透玲珑包",
    "提高队伍中所有共鸣者28%防御力，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Crystal_Clear_Buns"
)
db.add_food(
    "80001014",
    "昨日今州",
    "提高队伍中所有共鸣者10%攻击力和8%暴击率，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Yesterday_in_Jinzhou"
)
db.add_food(
    "80001016",
    "蓬蓬烘蛋",
    "提高队伍中所有共鸣者33%攻击力，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Fluffy_Wuthercake"
)
db.add_food(
    "80001017",
    "灿金炒饭",
    "减少队伍中所有共鸣者24%纵跑、游泳耐力消耗，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Golden_Fried_Rice"
)
db.add_food(
    "80001020",
    "眠花粥",
    "提高队伍中所有共鸣者24%暴击率，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Floral_Porridge"
)
db.add_food(
    "80001021",
    "咩咩酥",
    "提高队伍中所有共鸣者40%防御力，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Baa_Baa_Crisp"
)
db.add_food(
    "80001023",
    "金银莲子羹",
    "提高队伍中所有共鸣者33%生命上限，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Lotus_Seed_Soup"
)
db.add_food(
    "80001024",
    "果木烟熏鸽",
    "提高队伍中所有共鸣者55%防御力，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Smoked_Pigeon"
)
db.add_food(
    "80001025",
    "冠军冒菜",
    "提高队伍中所有共鸣者30%暴击率，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Champion_Hotpot"
)
db.add_food(
    "80001029",
    "绿野锅",
    "提高队伍中所有共鸣者44%攻击力，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Green_Field_Pot"
)
db.add_food(
    "80001032",
    "雾茗",
    "提高队伍中所有共鸣者14%防御力和12%生命上限，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Misty_Tea"
)
db.add_food(
    "80001033",
    "迎春酥",
    "提高队伍中所有共鸣者36%暴击伤害，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Spring_Pastry"
)
db.add_food(
    "80001034",
    "炽翎辣肉",
    "提高队伍中所有共鸣者24%共鸣效率，持续时间30分钟，在多人游戏中仅对自己的角色生效。",
    1800,
    "Blazing_Feather_Spicy_Meat"
)

consumables = db
