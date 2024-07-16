import re
from config import config
from enum import Enum

class AttributeWeight(Enum):
  暴击 = 6
  暴击伤害 = 3
  大攻击 = 4
  攻击 = 1
  共鸣技能伤害加成 = 0.5
  重击伤害加成 = 0.5
  普攻伤害加成 = 0.5
  共鸣解放伤害加成 = 0.5
  共鸣效率 = 0.5

def calculate_total_weight(paired_results, character_name=""):
  total_weight = 0.0
  adjusted_total_weight = 0.0
  max_total_weight = 0.0
  max_adjusted_total_weight = 0.0

  print(f"角色名: {character_name}")

  # 默认权重
  attribute_weights = {name: member.value for name, member in AttributeWeight.__members__.items()}
  adjusted_weights = attribute_weights.copy()
  print(f"默认权重: {attribute_weights}")
  # 根据角色名调整权重
  if character_name in Character.__members__:
    special_attribute = Character[character_name].value
    adjusted_weights[special_attribute] = 2.5
    print(f"调整后权重: {adjusted_weights}")
  for attribute, value in paired_results:
    if attribute in attribute_weights:
      weight = attribute_weights[attribute]
      adjusted_weight = adjusted_weights[attribute]
      # 使用正则表达式提取数字部分
      numeric_value_match = re.search(r'\d+(\.\d+)?', value)
      if numeric_value_match:
        numeric_value = float(numeric_value_match.group())
        print(f"{attribute}: {value}")
        total_weight += weight * numeric_value
        adjusted_total_weight += adjusted_weight * numeric_value
        # 计算最大值
        max_value_match = re.search(r'\d+(\.\d+)?', AttributeMax[attribute].value)
        if max_value_match:
          max_numeric_value = float(max_value_match.group())
          max_total_weight += weight * max_numeric_value
          max_adjusted_total_weight += adjusted_weight * max_numeric_value
  total_weight = round(total_weight, 2)
  adjusted_total_weight = round(adjusted_total_weight, 2)
  max_total_weight = round(max_total_weight, 2)
  max_adjusted_total_weight = round(max_adjusted_total_weight, 2)
  return total_weight, adjusted_total_weight if total_weight != adjusted_total_weight else None, max_total_weight, max_adjusted_total_weight

class Character(Enum):
  今汐 = "共鸣技能伤害加成"
  忌炎 = "重击伤害加成"

class AttributeMax(Enum):
  暴击 = "10.5%"
  暴击伤害 = "21%"
  大攻击 = "11.6%"
  攻击 = "50"
  共鸣技能伤害加成 = "11.6%"
  重击伤害加成 = "11.6%"
  普攻伤害加成 = "11.6%"
  共鸣解放伤害加成 = "11.6%"
  共鸣效率 = "12.4% "