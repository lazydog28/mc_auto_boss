# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: compute.py
@time: 2024/7/13 1.53
@author Ezhixuan
"""
import time

from . import *
import sys

pages = []


def compute(positions: dict[str, Position]) -> bool:
  """
  声骸计算
  :param positions: 角色位置信息
  :return: bool
  """

  if role_equip_points() is False:
    print("\n分值计算结束，请按下F12退出脚本，如需继续请重新打开脚本。")
    sys.exit(0)
    # 按下F12退出脚本
    control.tap(Key.F12)
  return True

compute_page = Page(
    name="声骸",
    targetTexts=[
      TextMatch(
          name="声",
          text="声",
      ),
      TextMatch(
          name="培养",
          text="培养",
      ),
    ],
    action=compute,
)

pages.append(compute_page)
