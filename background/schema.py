# -*- coding: utf-8 -*-
"""
@software: PyCharm
@file: schema.py
@time: 2024/6/4 上午10:18
@author SuperLazyDog
"""
import time

from pydantic import BaseModel, Field
from typing import Callable, Any, Dict, List
from datetime import datetime
import numpy as np
from re import Pattern, template
from PIL import Image
import cv2
from constant import width_ratio, height_ratio
from status import logger, info


class Position(BaseModel):
    x1: int = Field(None, title="x1")
    y1: int = Field(None, title="y1")
    x2: int = Field(None, title="x2")
    y2: int = Field(None, title="y2")

    def __call__(self):
        return (self.x1, self.y1), (self.x2, self.y2)

    def __str__(self):
        return f"({self.x1}, {self.y1}, {self.x2}, {self.y2})"

    def __repr__(self):
        return f"({self.x1}, {self.y1}, {self.x2}, {self.y2})"


class ImgPosition(Position):
    confidence: float = Field(0, title="识别置信度")


class OcrResult(BaseModel):
    text: str = Field(title="识别结果")
    position: Position = Field(title="识别位置")
    confidence: float = Field(0, title="识别置信度")


class TextMatch(BaseModel):
    name: str | None = Field(None, title="文本匹配名称")
    text: str | Pattern = Field(title="文本")
    position: Position | None = Field(None, title="文本范围位置，(x1, y1, x2, y2)")

    def __init__(self, /, **data: Any):
        super().__init__(**data)
        if isinstance(self.text, str):  # 如果文本是字符串，则转换为正则表达式
            self.text = template(self.text)


class ImageMatch(BaseModel):
    name: str | None = Field(None, title="图片匹配名称")
    image: str | np.ndarray = Field(title="图片")
    position: Position | None = Field(None, title="限定图片范围，(x1, y1, x2, y2)")
    confidence: float = Field(0.8, title="图片置信度", ge=0, le=1)

    def __init__(self, /, **data: Any):
        super().__init__(**data)
        if isinstance(self.image, str):  # 如果图片是路径，则读取图片
            self.image = np.array(Image.open(self.image))

    class Config:
        arbitrary_types_allowed = True


def match_template(
        img: np.ndarray, template_img: np.ndarray, threshold: float = 0.8
) -> None | ImgPosition:
    """
    使用 opencv matchTemplate 方法 模板匹配 返回匹配结果
    :param img:  大图片
    :param template_img: 小图片
    :param threshold:  阈值
    :return:
    """
    # 判断是否为灰度图，如果不是转换为灰度图
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if len(template_img.shape) == 3:
        template_img = cv2.cvtColor(template_img, cv2.COLOR_BGR2GRAY)

    # 将  template 进行缩放
    template_img = cv2.resize(template_img, (0, 0), fx=width_ratio, fy=height_ratio)

    res = cv2.matchTemplate(img, template_img, cv2.TM_CCOEFF_NORMED)
    confidence = np.max(res)
    if confidence < threshold:
        return None
    maxLoc = np.where(res == confidence)
    return ImgPosition(
        x1=maxLoc[1][0],
        y1=maxLoc[0][0],
        x2=maxLoc[1][0] + template_img.shape[1],
        y2=maxLoc[0][0] + template_img.shape[0],
        confidence=confidence,
    )


def is_position_contained(container: Position, contained: Position) -> bool:
    """
    判断一个位置是否被另一个位置完全包含。
    :param container:  大位置
    :param contained:  小位置
    :return:  bool
    """
    if container.x1 is not None and container.x1 * width_ratio > contained.x1:
        return False
    if container.y1 is not None and container.y1 * height_ratio > contained.y1:
        return False
    if container.x2 is not None and container.x2 * width_ratio < contained.x2:
        return False
    if container.y2 is not None and container.y2 * height_ratio < contained.y2:
        return False
    return True


def text_match(textMatch: TextMatch, ocrResults: List[OcrResult]) -> Position | None:
    """
    文本匹配
    :param textMatch: 文本匹配
    :param ocrResults:  ocr 识别结果
    :return:
    """
    for ocrResult in ocrResults:
        if textMatch.text.search(ocrResult.text):
            if textMatch.position is not None and not is_position_contained(
                    textMatch.position, ocrResult.position,
            ):
                continue
            return ocrResult.position
    return None


def image_match(imageMatch: ImageMatch, img: np.ndarray) -> Position | None:
    """
    图片匹配
    :param imageMatch: 图片匹配
    :param img:  图片
    :return:
    """
    imgPosition = match_template(img, imageMatch.image, imageMatch.confidence)
    if imgPosition is not None:
        if imageMatch.position is not None and not is_position_contained(
                imageMatch.position, imgPosition
        ):
            return None
        return imgPosition


class Page(BaseModel):
    name: str = Field(None, title="页面名称")
    action: Callable[[Dict[str, Position]], bool] = Field(title="页面操作函数")

    targetTexts: List[TextMatch] = Field([], title="目标文本")
    excludeTexts: List[TextMatch] = Field([], title="排除目标文本")

    targetImages: List[ImageMatch] = Field([], title="目标图片")
    excludeImages: List[ImageMatch] = Field([], title="排除目标图片")

    matchPositions: Dict[str, Position] = Field({}, title="匹配位置")

    def __init__(self, /, **data: Any):
        super().__init__(**data)

    class Config:
        arbitrary_types_allowed = True

    def __call__(self, img: np.ndarray, ocrResults: List[OcrResult]) -> bool:
        """
        页面匹配
        :param img: 游戏画面截图
        :param ocrResults:  游戏画面识别结果
        :param execute:  是否执行操作
        :return:  bool
        """
        # 清空匹配位置
        self.matchPositions = {}
        for (
                textMatch
        ) in (
                self.targetTexts
        ):  # 遍历目标文本 如果匹配到目标文本则记录位置 否则返回False
            if position := text_match(textMatch, ocrResults):
                self.matchPositions[textMatch.name] = position
            else:
                return False
        for (
                textMatch
        ) in self.excludeTexts:  # 遍历排除文本 如果匹配到排除文本则返回False
            if text_match(textMatch, ocrResults):
                return False
        for (
                imageMatch
        ) in (
                self.targetImages
        ):  # 遍历目标图片 如果匹配到目标图片则记录位置 否则返回False
            if position := image_match(imageMatch, img):
                self.matchPositions[imageMatch.name] = position
            else:
                return False
        for (
                imageMatch
        ) in self.excludeImages:  # 遍历排除图片 如果匹配到排除图片则返回False
            if image_match(imageMatch, img):
                return False
        return True


class ConditionalAction(BaseModel):
    name: str = Field(None, title="条件操作名称")
    condition: Callable[[], bool] = Field(title="条件函数")
    action: Callable[[], bool] = Field(title="操作函数列表")

    class Config:
        arbitrary_types_allowed = True

    def __call__(self) -> bool | None:
        if self.condition is None:
            raise Exception("条件函数未设置")
        if self.condition():
            return True
        else:
            return False


class Task(BaseModel):
    name: str = Field(None, title="任务名称")
    finished: bool = Field(False, title="任务是否完成")
    startTime: datetime = Field(datetime.now(), title="任务开始时间")
    timeoutTime: int = Field(0, title="任务超时时间")
    lastTime: datetime = Field(datetime.now(), title="任务最近一次执行时间")
    pages: list[Page] = Field([], title="任务页面")
    conditionalActions: list[ConditionalAction] = Field([], title="条件操作函数列表")

    class Config:
        arbitrary_types_allowed = True

    def __str__(self):
        return f"任务名称：{self.name} 开始时间：{self.startTime} 任务完成：{self.finished}"

    def __repr__(self):
        return f"任务名称：{self.name} 开始时间：{self.startTime} 任务完成：{self.finished}"

    # 判断任务是否超时
    def is_timeout(self):
        return (datetime.now() - self.startTime).seconds > self.timeoutTime

    # 添加条件任务函数
    def add_conditional_actions(
            self, condition: Callable[[], bool], actions: List[Callable[[], Any]]
    ):
        self.conditionalActions.append(
            ConditionalAction(condition=condition, actions=actions)
        )

    # 添加页面
    def add_page(self, page: Page):
        self.pages.append(page)

    # 被调用时执行任务
    def __call__(self, img: np.ndarray, ocrResults: List[OcrResult]):
        for page in self.pages:
            match_page = page(img, ocrResults)
            if match_page:
                info.currentPageName = page.name
                if page.name != "声骸":
                    logger(f"当前页面：{page.name}")
                page.action(page.matchPositions)
        for conditionalAction in self.conditionalActions:
            match_conditional_action = conditionalAction()
            if match_conditional_action:
                logger(f"当前条件操作：{conditionalAction.name}")
                conditionalAction.action()
