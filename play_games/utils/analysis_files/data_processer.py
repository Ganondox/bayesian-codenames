import os
import warnings

import numpy as np
import joblib
import scipy.stats as stats
from play_games.utils import utils
from play_games.configs.experiment_settings import ExperimentSettings

from play_games.paths import file_paths
from play_games.utils.analysis_files.analysis_utils import Stats, StatDictKeys, save_json, load_json
from play_games.configs.enums import ExperimentType

class DataProcessor:
    def __init__(self, experiment_settings: ExperimentSettings, experiment_paths: file_paths.ExperimentPaths):
        self.experiment_paths = experiment_paths
        self.experiment_settings = experiment_settings
        self.confidence_level = .95

    def process_data(self, parsed_data, processed_data_filepaths):
            processed_data = {}
            
            #I need a dictionary for holding all of the data across learn periods

            #At this point, we know that our data is parsed and loaded into the corred class variables 

            #Do the round log specific processing
            #win rate, avg win time, min win time, pair scores, avg red, blue, bys, assas flipped by game
            
            #loop through lps, cms, and gs and then calculate all of the scores
            for lp in parsed_data:
                processed_data[lp] = {}
                for cm in parsed_data[lp]:
                    processed_data[lp][cm] = {}
                    for g in parsed_data[lp][cm]:
                        processed_data[lp][cm][g] = {}
                        #For each learning period and for each pairing, calculate stats
                        data = parsed_data[lp][cm][g]

                        #calculate lp win rate
                        processed_data[lp][cm][g][Stats.WIN_RATE] = np.average(data[Stats.GAME_WIN_LOSS])

                        #calculate lp avg win time
                        win_times = self.get_win_times(data[Stats.GAME_WIN_LOSS], data[Stats.NUM_ROUNDS_PER_GAME])

                        turns_per_game = data[Stats.NUM_ROUNDS_PER_GAME]

                        if len(win_times) != 0: processed_data[lp][cm][g][Stats.AVG_WIN_TIME] = np.average(win_times)
                        else: processed_data[lp][cm][g][Stats.AVG_WIN_TIME] = 25.0

                        processed_data[lp][cm][g][Stats.AVG_TURNS_BY_GAME] = np.average(turns_per_game)
                        processed_data[lp][cm][g][Stats.TURNS_BY_GAME] = turns_per_game

                        #calculate lp avg red words flipped per game
                        flips = self.calculate_flips_by_game(parsed_data, Stats.RED_WORDS_FLIPPED_BY_ROUND, lp, cm, g)
                        processed_data[lp][cm][g][Stats.RED_FLIP_BY_GAME] = flips
                        processed_data[lp][cm][g][Stats.AVG_RED_FLIP_BY_GAME] = np.average(flips)

                        #calculate lp avg blue words flipped per game
                        flips = self.calculate_flips_by_game(parsed_data, Stats.BLUE_WORDS_FLIPPED_BY_ROUND, lp, cm, g)
                        processed_data[lp][cm][g][Stats.BLUE_FLIP_BY_GAME] = flips
                        processed_data[lp][cm][g][Stats.AVG_BLUE_FLIP_BY_GAME] = np.average(flips)

                        #calculate lp avg bystander words flipped per game
                        flips = self.calculate_flips_by_game(parsed_data, Stats.BYSTANDER_WORDS_FLIPPED_BY_ROUND, lp, cm, g)
                        processed_data[lp][cm][g][Stats.BYSTANDER_FLIP_BY_GAME] = flips
                        processed_data[lp][cm][g][Stats.AVG_BYSTANDER_FLIP_BY_GAME] = np.average(flips)

                        #calculate lp avg assassin words flipped per game
                        flips = self.calculate_flips_by_game(parsed_data, Stats.ASSASSIN_WORDS_FLIPPED_BY_ROUND, lp, cm, g)
                        processed_data[lp][cm][g][Stats.ASSASSIN_FLIP_BY_GAME] = flips
                        processed_data[lp][cm][g][Stats.AVG_ASSASSIN_FLIP_BY_GAME] = np.average(flips)

                        #calculate cm or g learn stats if it is a learning experiment with either an ensemble cm or g
                        if len(self.experiment_paths.learn_log_filepaths_cm) > 0:
                            self.process_learning_data(processed_data, parsed_data, lp, cm, g, StatDictKeys.CM_LEARN_STATS)
                        if len(self.experiment_paths.learn_log_filepaths_g) > 0:
                            self.process_learning_data(processed_data, parsed_data, lp, cm, g, StatDictKeys.G_LEARN_STATS)

            #save the data for individual files
            for counter in parsed_data.keys():
                filepath = processed_data_filepaths[counter]
                save_json(processed_data[counter], filepath)

            return processed_data

    def get_win_times(self, game_win_loss, num_rounds_per_game):
        win_times = []
        for i in range(len(game_win_loss)):
            if game_win_loss[i] == 1:
                win_times.append(int(num_rounds_per_game[i]))
        return win_times
    
    def calculate_flips_by_game(self, parsed_data, key, lp, cm, g):
        curr_pos = 0
        flips_in_game = []
        for rounds_in_game in parsed_data[lp][cm][g][Stats.NUM_ROUNDS_PER_GAME]:
            flipped_in_game = 0
            for i in range(curr_pos, curr_pos + rounds_in_game):
                flipped_in_game += parsed_data[lp][cm][g][key][i]
            flips_in_game.append(flipped_in_game)
            curr_pos += rounds_in_game
        return flips_in_game

    
    def process_learning_data(self, processed_data, parsed_data, lp, cm, g, key):
        if key not in parsed_data[lp][cm][g]:
            return 
        #Add a new key into the data structure
        processed_data[lp][cm][g][key] = {}

        if key not in parsed_data[lp][cm][g]:
            return

        #Check the percentages of each bot chosen
        bots_chosen = parsed_data[lp][cm][g][key][Stats.CHOSEN_BOTS_BY_ROUND]
        bot_counts = {}
        for bot in bots_chosen:
            if bot not in bot_counts:
                bot_counts[bot] = 1
            else:
                bot_counts[bot] += 1
        
        for bot in bot_counts:
            bot_counts[bot] = bot_counts[bot] / len(bots_chosen)

        processed_data[lp][cm][g][key][Stats.PERCENTAGE_BOT_CHOSEN] = bot_counts

        #Now we need to find the arm weights by game
        processed_data[lp][cm][g][key][Stats.ARM_WEIGHTS_BY_GAME] = self.calculate_arm_weights_by_game(parsed_data, lp, cm, g, key)

    def load_processed_data(self):
        processed_data = {}
        counter = 0
        for filepath in self.experiment_paths.processed_data_filepaths[:-1]:
            try:
                processed_data[counter] = load_json(filepath)
            except:
                counter += 1
                continue
            counter += 1
        processed_data[StatDictKeys.FINAL_KEY] = load_json(self.experiment_paths.processed_data_filepaths[-1])

        return processed_data