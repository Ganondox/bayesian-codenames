
from play_games.bots.ai_components.associator_ai_components.vector_data_cache import VectorDataCache
from play_games.bots.bot_settings_obj import BotSettingsObj
from play_games.bots.guessers.guesser import Guesser


class VectorBaselineGuesser(Guesser):
    def __init__(self):
        pass

    def initialize(self, bot_settings_obj: BotSettingsObj):
        if isinstance(bot_settings_obj.CONSTRUCTOR_PATHS, (list, tuple)):
            self.vectors = VectorDataCache(*bot_settings_obj.CONSTRUCTOR_PATHS)
        else:
            self.vectors = VectorDataCache(bot_settings_obj.CONSTRUCTOR_PATHS)
            
    def guess_clue(self, clue, num_guess, prev_guesses):
        board_words = [w for w in self.board_words if w not in prev_guesses]
        return self._get_n_closest_words(num_guess, clue, board_words)

    def load_dict(self, words):
        self.board_words = words.copy()

    def give_feedback(self, *_):
        pass

    def _get_n_closest_words(self, n, clue, words):
        return sorted(words, key=lambda w: self.vectors.distance_word(clue, w))[:n]
