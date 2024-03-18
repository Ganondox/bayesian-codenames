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
    BYSTANDER = 2
    ASSASSIN = 3

    def team(color):
        return Color(color)
    
    def opponent(color):
        return Color((color+1)%2)