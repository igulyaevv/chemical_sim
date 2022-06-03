from enum import Enum

# Algorithms
DEFAULT = "Обычный запуск"
DOWNHILL = "Покоординатный спуск"
TPE = "TPE"

RESIZE = 3


class Modes(str, Enum):
    CONST = "Постояннотоковый"
    VAR = "Переменнотоковый"


class Status(Enum):
    ON_SURFACE = "На поверхности"
    BREAKING_AWAY = "Отделяется от поверхности"
    UP_ALONG_SURFACE = "Двигается вверх вдоль поверхности"
    DOWN_ALONG_SURFACE = "Двигается вниз вдоль поверхности"
    MERGING = "Проходит (прошел) слияние с другим кластером"
    OFF_SURFACE = "Находится вне поверхности"
