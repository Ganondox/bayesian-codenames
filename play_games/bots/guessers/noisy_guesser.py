
from play_games.bots.ai_components.associator_ai_components.vector_data_cache import VectorDataCache, distance_vec
from play_games.bots.bot_settings_obj import BotSettingsObj
from play_games.bots.guessers.guesser import Guesser
from play_games.bots.ai_components import vector_utils

class NoisyGuesser(Guesser):
    def __init__(self):
        pass

    def initialize(self, bot_settings_obj: BotSettingsObj):
        if isinstance(bot_settings_obj.CONSTRUCTOR_PATHS, (list, tuple)):
            self.vectors = VectorDataCache(*bot_settings_obj.CONSTRUCTOR_PATHS)
        else:
            self.vectors = VectorDataCache(bot_settings_obj.CONSTRUCTOR_PATHS)
        
        self.std = bot_settings_obj.EMBEDDING_NOISE
            
    def guess_clue(self, clue, num_guess, prev_guesses):
        board_words = [w for w in self.board_words if w not in prev_guesses]
        return self._get_n_closest_words(num_guess, clue, board_words)

    def load_dict(self, words):
        self.board_words = words.copy()

    def give_feedback(self, *_):
        pass

    def _get_n_closest_words(self, n, clue, words):
        noisy_clue = vector_utils.perturb_embedding(self.vectors[clue], self.std)
        dists = [distance_vec(noisy_clue, self.vectors[w]) for w in words]
        return [words[i] for i in sorted(range(len(words)), key=dists.__getitem__)[:n]]