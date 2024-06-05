# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: __init__.py.py
@time: 2024/6/5 上午9:34
@author SuperLazyDog
"""
from schema import Position, ImgPosition, OcrResult, TextMatch, ImageMatch, Page
from control import control
from re import Pattern, template
from status import info, Status, logger
from datetime import datetime
from utils import *
import time