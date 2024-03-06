from abc import ABC, abstractmethod

from play_games.bots.bot_settings_obj import BotSettingsObj
from play_games.games.enums import Color, GameCondition


class Guesser(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def initialize(self, bot_settings_obj: BotSettingsObj):
        pass

    @abstractmethod
    def guess_clue(self, clue, num_guess, prev_guesses)->list[str]:
        raise NotImplementedError()

    @abstractmethod
    def load_dict(self, words: list[str]):
        pass

    @abstractmethod
    def give_feedback(self, end_status: GameCondition, word_type: Color):
        pass