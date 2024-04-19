import heapq
import random
from typing import Self
from play_games.bots.ai_components.associator_ai_components.associator_data_cache import AssociatorDataCache
from play_games.bots.ai_components.associator_ai_components.vector_data_cache import VectorDataCache
from play_games.bots.types import LMType
from play_games.games.enums import Color
from play_games.paths import bot_paths


LANGUAGE_MODELS = [LMType.W2V,]# LMType.GLOVE_300, LMType.CN_NB, LMType.D2V, LMType.FAST_TEXT]

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
    

class InternalSpymaster:

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

    def reset(self, boardwords):
        self.boardwords = list(boardwords)
        possible_clues = self.possible_clues(boardwords)
        self.sorted_words = {
            clue:
            heapq.nsmallest(9, [(self.vectors.distance_word(clue, w), w) for w in boardwords])
            for clue in possible_clues
        }

    def get_clue(self, state, boardwords, num_left)->tuple[str, int]:
        possible_clue_words = self.possible_clues(boardwords, state)
        boardwords = set(boardwords)
        max_clue_word, max_size_num, min_dist = None, 0, float('inf')
        num_player = sum(1 for w in boardwords if state[w] == Color.TEAM)

        for clue in possible_clue_words:
            sort = []
            for info in self.sorted_words[clue]:
                if info[1] not in boardwords:
                    continue
                if len(sort) == num_player:
                    break
                sort.append(info)

            num = 0
            dist = 0
            for d, w in sort:
                if state[w] != Color.TEAM:
                    break
                num+=1
                dist+=d

            if num != 0 and num >= max_size_num and (num != max_size_num or dist < min_dist):
                max_clue_word, max_size_num, min_dist = clue, num, dist
            
        if max_clue_word == None:
            return random.choice(possible_clue_words), 1
        else:
            return max_clue_word, max_size_num

    def possible_clues(self, boardwords, state=None):
        possible_clue_words = set()
        possible_clue_words.update(*[self.associations[w] for w in boardwords if state is None or state[w] == Color.TEAM])
        return list(possible_clue_words)

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