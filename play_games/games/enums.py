import enum


class GameCondition(enum.IntEnum):
    """Enumeration that represents the different states of the game"""
    CONTINUE = 0
    LOSS = 1
    WIN = 2


class Color(enum.IntEnum):
    TEAM = 0
    OPPONENT = 1

    RED = 0
    BLUE = 1
    BYST = 2
    ASSA = 3