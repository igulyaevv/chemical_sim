from enum import Enum


class Algorithm(str, Enum):
    DEFAULT = "Обычный запуск"
    DOWNHILL = "Покоординатный спуск"
    TPE = "TPE"


class UISize(int, Enum):
    WIN_W = 1280
    WIN_H = 720
    SIDEBAR_W = 200
    SIDEBAR_H = 720
    GRAPHBAR_W = 400
    GRAPHBAR_H = 360
    STATBAR_W = 400
    STATBAR_H = 360
    CANVAS_W = 680
    CANVAS_H = 720


RESIZE = 3


class Mode(str, Enum):
    CONST = "Постояннотоковый"
    VAR = "Переменнотоковый"


class Status(str, Enum):
    ON_SURFACE = "На поверхности"
    BREAKING_AWAY = "Отделяется от поверхности"
    UP_ALONG_SURFACE = "Двигается вверх вдоль поверхности"
    DOWN_ALONG_SURFACE = "Двигается вниз вдоль поверхности"
    MERGING = "Проходит (прошел) слияние с другим кластером"
    OFF_SURFACE = "Находится вне поверхности"
