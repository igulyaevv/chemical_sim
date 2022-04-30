from enum import Enum

# Modes
CONST = "Постояннотоковый"
VAR = "Переменнотоковый"

# Algorithms
DEFAULT = "Обычный запуск"
DOWNHILL = "Покоординатный спуск"
TPE = "TPE"

RESIZE = 3


class Status(Enum):
    ON_SURFACE = 1
    BREAKING_AWAY = 2
    UP_ALONG_SURFACE = 3
    DOWN_ALONG_SURFACE = 4
    MERGING = 5
    OFF_SURFACE = 6
