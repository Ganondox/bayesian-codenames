
from copy import deepcopy
import heapq
import random
from bots.ai_components.associator_ai_components.distance_associator import DistanceAssociator
import numpy as np

from play_games.bots.ai_components.associator_ai_components.associator_data_cache import AssociatorDataCache
from play_games.bots.ai_components.associator_ai_components.vector_data_cache import VectorDataCache
from play_games.bots.bot_settings_obj import BotSettingsObj
from play_games.bots.spymasters.spymaster import Spymaster
from play_games.bots.types import BotType
from play_games.games.enums import Color
from play_games.paths import bot_paths
from play_games.bots.ai_components import vector_utils

class NoisySpymaster(Spymaster):
    def __init__(self, lm):
        self.lm = lm
        

    def initialize(self, settings_obj: BotSettingsObj):
        vector_filepath = bot_paths.get_vector_path_for_lm(self.lm),
        associations_filepath = bot_paths.get_association_path_for_lm(self.lm)
        if isinstance(vector_filepath, (tuple, list)):
            self.vectors = VectorDataCache(*vector_filepath)
        else:
            self.vectors = VectorDataCache(vector_filepath)
        self.associations = AssociatorDataCache(associations_filepath,)
        self.associations.load_cache(settings_obj.N_ASSOCIATIONS)
        self.noise = settings_obj.NOISE_SM

    def load_dict(self, boardwords):
        self.boardwords = list(boardwords)
        possible_clues = self.get_possible_clues(boardwords)
        self.sorted_words = {
            clue:
            heapq.nsmallest(9, [(self.vectors.distance_word(clue, w), w) for w in boardwords])
            for clue in possible_clues
        }

    def generate_clue(self, state, boardwords)->tuple[str, int]:
        possible_clues = self.get_possible_clues(boardwords, state)
        boardwords = set(boardwords)
        max_clue_word, max_size_num, min_dist = None, 0, float('inf')
        num_player = sum(1 for w in boardwords if state[w] == Color.TEAM)
        for clue in possible_clues:
            num = 0
            dist = 0
            for d, w in self.sorted_words[clue]:
                if w not in boardwords: continue
                if num == num_player or state[w] != Color.TEAM: break
                num+=1
                dist+=d

            if num != 0 and num >= max_size_num and (num != max_size_num or dist < min_dist):
                max_clue_word, max_size_num, min_dist = clue, num, dist
            
        if max_clue_word == None:
            max_clue_word, max_size_num = random.choice(possible_clues), 1
        
        return self._add_noise(max_clue_word), max_size_num

    def give_feedback(self, guess: str, color: Color, end_status):
        pass

    def get_possible_clues(self, boardwords, state=None):
        possible_clue_words = set()
        possible_clue_words.update(*[self.associations[w] for w in boardwords if state is None or state[w] == Color.TEAM])
        possible_clue_words.difference_update(self.boardwords)
        return list(possible_clue_words)
    
    def _add_noise(self, word):
        if self.noise == 0:
            return word
        
        noisy = vector_utils.perturb_embedding(self.vectors[word], self.noise)
        associations = [self.vectors[w] for w in self.associations[word]]
        associations.append(self.vectors[word])
        dists: np.ndarray = np.linalg.norm(associations - noisy, axis=1)
        min_i = dists.argmin()

        if min_i == len(associations)-1:
            return word
        else:
            return self.associations[word][min_i]


    def __desc__(self):
        return f"{BotType.NOISY_SPYMASTER}:{self.lm}:{self.noise}"

    def __hash__(self) -> int:
        return hash(self.lm)
    
    def __eq__(self, other):
        return hasattr(other, "lm") and other.lm == self.lm
    
    def __str__(self):
        return self.lm.__str__()
    
    def __repr__(self):
        return self.lm.__str__()