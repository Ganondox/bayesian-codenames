import heapq
import random
from typing import Self
from play_games.bots.ai_components.associator_ai_components.associator_data_cache import AssociatorDataCache
from play_games.bots.ai_components.associator_ai_components.vector_data_cache import VectorDataCache
from play_games.bots.types import LMType
from play_games.games.enums import Color
from play_games.paths import bot_paths


LANGUAGE_MODELS = [LMType.W2V, LMType.GLOVE_300, LMType.CN_NB, LMType.D2V]

class InternalGuesser:

    def __init__(self, lm, n_assoc):
        self.lm = lm
        vector_filepath = bot_paths.get_vector_path_for_lm(lm),
        associations_filepath = bot_paths.get_association_path_for_lm(lm)
        if isinstance(vector_filepath, (tuple, list)):
            self.vectors = VectorDataCache(*vector_filepath)
        else:
            self.vectors = VectorDataCache(vector_filepath)

        self.associations = AssociatorDataCache(associations_filepath,)
        self.associations.load_cache(n_assoc)


    def __hash__(self) -> int:
        return hash(self.lm)
    
    def __eq__(self, other):
        return hasattr(other, "lm") and other.lm == self.lm
    
    def __str__(self):
        return self.lm.__str__()
    
    def __repr__(self):
        return self.lm.__str__()
    
class WorldSampler():
    boardwords: list[str]
    current_state: dict[str, Color]
    team_left: int
    oppo_left: int
    byst_left: int
    assa_left: int
    covered_words: set[str]
    colors_left: list[Color]

    def reset(self, boardwords):
        self.boardwords = boardwords
        self.current_state = {w:None for w in boardwords}

        self.team_left, self.oppo_left, self.byst_left, self.assa_left = 9,8,7,1
        self.covered_words = set(self.boardwords)
        self.__compute_new_colors_left()

    def update_state(self, guesses, colors):
        for g, c in zip(guesses, colors):
            self.current_state[g] = c
            self.covered_words.remove(g)
            match c:
                case Color.TEAM:
                    self.team_left -= 1
                case Color.OPPONENT:
                    self.oppo_left -= 1
                case Color.BYSTANDER:
                    self.byst_left -= 1
                case Color.ASSASSIN:
                    self.assa_left -= 1
        self.__compute_new_colors_left()

    def sample_states(self, N):
        result = [self.current_state.copy() for _ in range(N)]
        for partial_state in result:
            random.shuffle(self.colors_left)
            partial_state.update(zip(self.covered_words, self.colors_left))
        return result
    
    def __compute_new_colors_left(self):
        self.colors_left = (
            [Color.TEAM] * self.team_left 
            + [Color.OPPONENT] * self.oppo_left
            + [Color.BYSTANDER] * self.byst_left
            + [Color.ASSASSIN] * self.assa_left
        )


class History:

    def reset(self):
        self._clue_history = []
        self._boardword_history = []
        self._player_cards_history = []
        self.rounds = 0

    def record(self, clue= None, boardwords=None, player_cards_left=None):
        self.rounds += 1
        self._clue_history.append(clue)
        self._boardword_history.append(boardwords)
        self._player_cards_history.append(player_cards_left)


    def get_record(self, time):
        return self._clue_history[time], self._boardword_history[time], self._player_cards_history[time]

    def __len__(self):
        return self.rounds
    
    def __iter__(self):
        yield from zip(self._clue_history, self._boardword_history, self._player_cards_history)