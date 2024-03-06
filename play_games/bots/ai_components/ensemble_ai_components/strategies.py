from copy import deepcopy
import random
import numpy as np
from play_games.utils import utils

#This strategy uses 36 features representing the probability of an individual turn outcome 
class StrategyThree(object):

        def __init__(self, ensamble_cm_instance):
            self.outer = ensamble_cm_instance
            self.model = utils.load_joblib_no_warnings(self.outer.bot_settings.MODEL_PATH)
            self.bot_stats = {}
            self.pos_events = []
            self.event_dict = {}

            self.red_flipped = 0
            self.blue_flipped = 0
            self.bystander_flipped = 0
            self.assassin_flipped = 0

        def select_bot(self):
            return max(self.outer.bot_weights, key=self.outer.bot_weights.get)

        def initialize_bot_stats(self):
            self.generate_pos_events()
            for bot in self.outer.bot_types:
                #I need to initalize a dictionary containing all of the possible turns and their counts for each bot
                self.outer.usage_dict[bot] = 0
                self.outer.bot_weights[bot] = np.inf
                self.bot_stats[bot] = self.event_dict.copy()

        def update_values(self):
            # I need to add the previous turn outcome to bot_stats
            self.add_prev_turn_result()
            for key in self.outer.bot_weights:
                total_rounds_used = self.outer.usage_dict[key] + 1

                curr_score = self.calculate_score(key) 
                
                self.outer.bot_weights[key] = curr_score + (self.outer.ucb_constant * (np.sqrt(np.log(self.outer.total_rounds) / total_rounds_used)))
            
            #We set the words flipped back to zero for next turn
            self.red_flipped = 0
            self.blue_flipped = 0
            self.bystander_flipped = 0
            self.assassin_flipped = 0

        def add_correct_consequence(self):
            self.red_flipped += 1
                
        def add_bystander_consequence(self):
            self.bystander_flipped += 1

        def add_opponent_consequence(self):
            self.blue_flipped += 1

        def add_assassin_consequence(self):
            self.assassin_flipped += 1

        ###---Strategy Helper Functions---###
        def add_prev_turn_result(self):
            #I need to create the correct key
            key = self.create_string(self.red_flipped, self.blue_flipped, self.bystander_flipped, self.assassin_flipped)
            #If we're on the first round, bots_used will be empty so we don't need to worry about indexing into a non-existent key. 
            for bot, weight in self.outer.bots_used.items():
                self.bot_stats[bot][key] += weight

        def get_x(self, key):
            total_events = sum(self.bot_stats[key].values())

            if total_events != 0:
                return [self.bot_stats[key][event] / total_events for event in self.pos_events]
            else:
                return [0]*len(self.pos_events)

        def calculate_score(self, key):
            #check to see if it's been used yet, if it hasn't, then it's score is infinity
            if self.outer.usage_dict[key] == 0:
                return np.inf
                
            x = self.get_x(key)
            y = self.model.predict([x])[0]
            return y

        def generate_pos_events(self):
            self.event_dict = {}
            for r in range(10):
                c = 0
                for b in [None, 'theirs', 'by', 'assassin']:
                    
                    if r == 0 and (b is None):
                        c += 1
                        continue
                    if r == 9 and (b is not None):
                        c += 1
                        continue

                    key = [r, 0, 0, 0]
                    if c > 0:
                        key[c] = 1
                    c += 1
                    key_str = self.create_string(*key)
                    self.pos_events.append(key_str)
                    self.event_dict[key_str] = 0

        def create_string(self, *arr):
            return ''.join(map(str, arr))
        
        def __deepcopy__(self, memo):
            cls = self.__class__
            result = cls.__new__(cls)
            memo[id(self)] = result
            memo[id(self.model)] = self.model
            for k, v in self.__dict__.items():
                setattr(result, k, deepcopy(v, memo))
            return result

#This strategy randomly selects an arm
class StrategyFour(object):

    def __init__(self, ensamble_cm_instance):
        self.outer = ensamble_cm_instance

    def select_bot(self):
        return random.choice(self.outer.bot_types)

    def initialize_bot_stats(self):
        for bot in self.outer.bot_types:
            #I need to initalize a dictionary containing all of the possible turns and their counts for each bot
            self.outer.usage_dict[bot] = 0
            self.outer.bot_weights[bot] = 0


    def update_values(self):
        pass

    def add_correct_consequence(self):
        pass
            
    def add_bystander_consequence(self):
        pass

    def add_opponent_consequence(self):
        pass

    def add_assassin_consequence(self):
        pass

