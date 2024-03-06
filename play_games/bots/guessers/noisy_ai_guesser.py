
from copy import deepcopy
from play_games.bots.ai_components import vector_utils
import scipy.spatial.distance

import numpy as np
from play_games.bots.guessers.guesser import Guesser

from play_games.utils.utils import quick_dist

class NoisyAIGuesser(Guesser):
    def __init__(self):
        pass
    
    def initialize(self, bot_settings_obj):
        if type(bot_settings_obj.CONSTRUCTOR_PATHS) == list:
            first_vecs_path = bot_settings_obj.CONSTRUCTOR_PATHS[0]
            second_vecs_path = bot_settings_obj.CONSTRUCTOR_PATHS[1]
        else:
            first_vecs_path = bot_settings_obj.CONSTRUCTOR_PATHS
            second_vecs_path = None

        self.embedding_noise = bot_settings_obj.EMBEDDING_NOISE 
        self.dist_noise = bot_settings_obj.DIST_NOISE
        
        self.first_vecs = vector_utils.load_vectors(first_vecs_path)
        self.second_vectors = {}
        if second_vecs_path:
            self.second_vectors = vector_utils.load_vectors(second_vecs_path)
        self.num = 0
        self.bot_type = bot_settings_obj.BOT_TYPE_G
    
    def guess_clue(self, clue, num_guess, prev_guesses):
        sorted_words = self.compute_distance(clue, [w for w in self.board_words if w not in prev_guesses])
        guesses = []
        for i in range(len(sorted_words[:num_guess])):
            guesses.append(sorted_words[i][1])
        return guesses

    def load_dict(self, words):
        self.board_words = words.copy()

    def give_feedback(self, guess, end_status):
        pass

    def compute_distance(self, clue, board):
        w2v = []
        if self.second_vectors:
            all_vectors = (self.second_vectors, self.first_vecs,)
        else:
            all_vectors = (self.first_vecs,)
        
        #apply noise to clue
        perturbed_clue = vector_utils.perturb_embedding(self.concatenate(clue, all_vectors), self.embedding_noise)
        
        for word in board:
            board_word = self.concatenate(word.lower(), all_vectors)
            
            # apply noise to distance
            dist = vector_utils.perturb_distance(quick_dist(perturbed_clue, board_word), self.dist_noise)

            w2v.append((dist, word))

        w2v = list(sorted(w2v))
        return w2v


    def concatenate(self, word, wordvecs):
        concatenated = wordvecs[0][word]
        for vec in wordvecs[1:]:
            concatenated = np.hstack((concatenated, vec[word]))
        return concatenated

    def give_feedback(self, val1, val2):
        pass
    
    def end_game(self, val):
      pass

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        if hasattr(self, "first_vecs"):
            memo[id(self.first_vecs)] = self.first_vecs
            memo[id(self.second_vectors)] = self.second_vectors
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result
    
    def __desc__(self):
        return f"Noisy {self.bot_type}:{self.embedding_noise}:{self.dist_noise}"