import abc
from typing import Any
from play_games.bots.bot_settings_obj import BotSettingsObj

from play_games.games.enums import GameCondition


class Spymaster(abc.ABC):
    @abc.abstractmethod
    def __init__(self):
        pass

    @abc.abstractmethod
    def initialize(self, settings_obj: BotSettingsObj|Any):
        pass
    
    @abc.abstractmethod
    def load_dict(self, boardwords: list[str]):
        pass
    
    @abc.abstractmethod
    def generate_clue(self, player_words, prev_clues, opponent_words, assassin_word, bystander_words)->tuple[str, list[str]]:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def give_feedback(self, guess: str, color: str, end_status: GameCondition):
        pass