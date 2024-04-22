
from copy import deepcopy
import random
from bots.ai_components.associator_ai_components.distance_associator import DistanceAssociator
import numpy as np

from play_games.bots.bot_settings_obj import BotSettingsObj
from play_games.bots.spymasters.spymaster import Spymaster
from play_games.games.enums import Color

class DistanceAssociatorAISpymaster(DistanceAssociator, Spymaster):
    def __init__(self):
        self.association_location_dict = None
        self.closest_bad_words = dict()
    
    def initialize(self, settings_obj: BotSettingsObj):
        super().__init__(settings_obj.N_ASSOCIATIONS, settings_obj.CONSTRUCTOR_PATHS[0], settings_obj.CONSTRUCTOR_PATHS[1])

    def load_dict(self, boardwords):
        self.closest_bad_words.clear()
        return super().load_dict(boardwords)
    
    def generate_clue(self, state, boardwords):
        # find max occurrence - this will be the clue (see fixme comment above)
        player_words, opponent_words, assassin_word, bystander_words = (
            [b for b in boardwords if state[b] == Color.TEAM],
            [b for b in boardwords if state[b] == Color.OPPONENT],
            [b for b in boardwords if state[b] == Color.ASSASSIN][0],
            [b for b in boardwords if state[b] == Color.BYSTANDER],
        )

        self.player_words = player_words
        bad_words = list(opponent_words)
        bad_words.extend(bystander_words)
        bad_words.append(assassin_word)

        self.association_location_dict = self.find_common_word_associations(player_words) 
        self.filter_unwanted_clues(bad_words)
        clue, target_words = self.find_best_clue()

        return clue, target_words

        # possible_clue_words = set()
        # for word in player_words:
        #     possible_clue_words.update(self.assoc_cache.associations[word])
        # possible_clue_words = tuple(possible_clue_words)

        # max_size_num = 0
        # max_clue_word = None
        # min_dist = float('inf')

        # for clue in possible_clue_words:
        #     dist_fn = lambda w: self.vectors.distance_word(clue, w)
        #     ranked_boardwords = sorted(player_words +  opponent_words + bystander_words +[assassin_word], key=dist_fn)

        #     num = 0
        #     dist = 0
        #     for w in ranked_boardwords:
        #         if num == len(player_words) or w not in player_words:
        #             break
        #         num+=1
        #         dist+=dist_fn(w)

        #     if num != 0 and num >= max_size_num and (num != max_size_num or dist < min_dist):
        #         max_clue_word = clue
        #         min_dist = dist
        #         max_size_num = num
            
        # if max_clue_word == None:
        #     return random.choice(possible_clue_words), ['None']
        # else:
        #     return max_clue_word, ['None']*max_size_num
    
    def find_best_clue(self): 
        #We must first order our dictionary
        # Primarily by number of associated words, secodarily by sum of targets
        best_clue = (None, 0, np.inf)

        for pos_clue in self.association_location_dict.keys():
            associated_board_words = self.association_location_dict[pos_clue]
            num_targets = len(associated_board_words)
            total_distance = sum(dist for _, dist in associated_board_words)
            
            if num_targets > best_clue[1] or (num_targets == best_clue[1] and total_distance < best_clue[2]):
                best_clue = (pos_clue, num_targets, total_distance)

        clue = best_clue[0]
        if clue is None:
            min_word = None
            min_clue = None
            min_val = np.inf
            for pos_clue in self.get_possible_clue_words(self.player_words):
                local_min_val, local_min_word = min((self.calculate_dist(pos_clue, w), w) for w in self.player_words)
                if local_min_val < min_val:
                    min_val = local_min_val
                    min_word = local_min_word
                    min_clue = pos_clue
            
            targets = [min_word]
            clue = min_clue
        else:
            targets = [target for target, _ in self.association_location_dict[clue]]
        return clue, targets
    
    def update_bad_distances(self, bad_words):
        bad_dists_dict = self.closest_bad_words
        for pos_clue in self.association_location_dict:
            if pos_clue in bad_dists_dict and bad_dists_dict[pos_clue][1] not in self.guessed: 
                continue

            worst_bad = np.inf
            worst_word = None
            for word in bad_words:
                curr_dist = self.calculate_dist(pos_clue, word)
                if curr_dist < worst_bad:
                    worst_bad = curr_dist
                    worst_word = word
            bad_dists_dict[pos_clue] = (worst_bad, worst_word)    
    
    def filter_unwanted_clues(self, badwords):
        #we filter out unwanted words (prev_clues and any association that has the assassin within the assassin_threshold and a blue word within
        # the blue_word_threshold)
        self.update_bad_distances(badwords)
        
        for pos_clue in tuple(self.association_location_dict.keys()):
            associated_board_words = self.association_location_dict[pos_clue]
            closest_bad = self.closest_bad_words[pos_clue][0]
            words_to_keep = [word_dist for word_dist in associated_board_words if word_dist[1] < closest_bad]

            if words_to_keep:
                self.association_location_dict[pos_clue] = words_to_keep
            else:
                del self.association_location_dict[pos_clue]