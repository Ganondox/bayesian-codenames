import numpy as np
import scipy.spatial.distance as dist
from copy import deepcopy
import bisect
from bots.ai_components.associator_ai_components.associator_data_cache import AssociatorDataCache
from bots.ai_components.associator_ai_components.vector_data_cache import VectorDataCache

class DistanceAssociator:
    assoc_cache: AssociatorDataCache
    vectors: VectorDataCache
    board_dict: dict[str, list]
    boardwords: list[str]

    def __init__(self, n, path, vector_path):
        self.assoc_cache = AssociatorDataCache(path)
        self.assoc_cache.load_cache(n)
        self.vectors = VectorDataCache(vector_path)
        self.board_dict = {}
        self.boardwords = []
        self.guessed = set()

    def load_dict(self, boardwords):
        self.boardwords = boardwords[:]
        self.guessed.clear()
        self.board_dict.clear()
        for word in boardwords:
            self.board_dict[word] = self.assoc_cache.get_associations(word)

    def give_feedback(self, word, *_):
        self.guessed.add(word)
    
    def calculate_dist(self, w1, w2):
        return self.vectors.distance_word(w1, w2)    
    
    def find_common_word_associations(self, player_words) -> dict[str, list[tuple[str, float]]]:
        #we create a dictionary of all associated words as keys and the word that they are associated to as a second key and 
        return_dict = {
            association: sorted(
                [
                    (word, self.calculate_dist(association, word)) 
                    for word in player_words
                ],
                key=lambda x:x[1]
            )

            for association in self.get_possible_clue_words(player_words)
        }

        return return_dict
    
    def get_possible_clue_words(self, player_words):
        assocs = [self.board_dict[word] for word in player_words]
        ret = set()
        ret.update(*assocs)
        return list(ret)
    
    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        if hasattr(self, "assoc_cache"):
            memo[id(self.assoc_cache)] = self.assoc_cache
            memo[id(self.vectors)] = self.vectors
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

