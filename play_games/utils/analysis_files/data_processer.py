import os
import warnings

import numpy as np
import joblib
import scipy.stats as stats
from play_games.utils import utils
from play_games.configs.experiment_settings import ExperimentSettings

from play_games.paths import file_paths
from play_games.utils.analysis_files.analysis_utils import Stats, StatDictKeys, FINAL_STAT_DIST_KEYS, save_json, load_json, MAIN_STATS_KEYS
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


                        if len(win_times) != 0: processed_data[lp][cm][g][Stats.AVG_WIN_TIME] = np.average(win_times)
                        else: processed_data[lp][cm][g][Stats.AVG_WIN_TIME] = 25.0

                        #calculate lp min win time
                        if len(win_times) != 0: processed_data[lp][cm][g][Stats.MIN_WIN_TIME] = min(win_times)
                        else: processed_data[lp][cm][g][Stats.MIN_WIN_TIME] = 25.0

                        #calculate lp pair scores (at the end of every game)
                        processed_data[lp][cm][g][Stats.PAIR_SCORES] = self.get_pair_scores(data[Stats.NUM_ROUNDS_PER_GAME], \
                            data[Stats.RED_WORDS_FLIPPED_BY_ROUND], data[Stats.BLUE_WORDS_FLIPPED_BY_ROUND], \
                            data[Stats.BYSTANDER_WORDS_FLIPPED_BY_ROUND], data[Stats.ASSASSIN_WORDS_FLIPPED_BY_ROUND])
                        
                        processed_data[lp][cm][g][Stats.FINAL_PAIR_SCORE] = processed_data[lp][cm][g][Stats.PAIR_SCORES][-1]

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
                        
                        self.get_running_averages(processed_data, parsed_data, lp, cm, g)
                        self.get_sliding_window_averages(processed_data, parsed_data, lp, cm, g)

            #If it is a learning experiment, we want to take averages across lps for stats and we store them in another file
            # if self.experiment_settings.experiment_type == ExperimentTypes.LEARNING_EXPERIMENT or self.experiment_settings.experiment_type == ExperimentTypes.PARAMETER_EXPERIMENT:
            if self.experiment_settings.experiment_type == ExperimentType.LEARNING_EXPERIMENT or \
                self.experiment_settings.experiment_type == ExperimentType.PARAMETER_EXPERIMENT:

                if self.experiment_settings.experiment_type == ExperimentType.LEARNING_EXPERIMENT:
                    processed_data[StatDictKeys.FINAL_KEY] = self.get_averages(processed_data)
                    self.add_final_distributions(processed_data)
                else:
                    processed_data[StatDictKeys.FINAL_KEY] = self.process_final_param_stats(processed_data)

                #Save the final data structure
                save_json(processed_data[StatDictKeys.FINAL_KEY], processed_data_filepaths[-1])

            #save the data for individual files
            for counter in parsed_data.keys():
                filepath = processed_data_filepaths[counter]
                save_json(processed_data[counter], filepath)

            return processed_data

    def process_final_param_stats(self, processed_data):
        #compile arrays for every cm, g pair and their stat 
        parameter_inds = list(processed_data.keys())
        cms = list(processed_data[parameter_inds[0]].keys())
        gs = list(processed_data[parameter_inds[0]][cms[0]])
        new = {}
        avg_key = "avg"
        
        for stat in MAIN_STATS_KEYS:
            all_vals = []
            for cm in cms:
                for g in gs:
                    pair_vals = []
                    for p in parameter_inds:
                        v = processed_data[p][cm][g][stat]
                        pair_vals.append(v)
                    all_vals.append(pair_vals)
                    if cm not in new:
                        new[cm] = {}
                    if g not in new[cm]:
                        new[cm][g] = {}
                    new[cm][g][stat] = pair_vals
            #now we get the average for each column
            all_vals = np.array(all_vals)
            means = []
            for i in range(len(all_vals[0])):
                means.append(np.mean(all_vals[:, i]))
            
            if avg_key not in new:
                new[avg_key] = {}
            new[avg_key][stat] = means
        
        return new

                    

    def add_final_distributions(self, processed_data):
        keys = list(processed_data.keys())
        keys = [k for k in keys if k != StatDictKeys.FINAL_KEY]
        for cm in processed_data[keys[0]]:
            for g in processed_data[keys[0]][cm]:
                #for each stat
                for s in FINAL_STAT_DIST_KEYS:
                    if type(s) == list and s[0] in processed_data[key][cm][g]:
                        new_stat = Stats.FINAL_STAT_DIST + " ~ " + s[1]
                        if new_stat not in processed_data[StatDictKeys.FINAL_KEY][cm][g][s[0]]:
                            processed_data[StatDictKeys.FINAL_KEY][cm][g][s[0]][new_stat] = {}
                        
                        for key in keys:
                            percentages_selected = processed_data[key][cm][g][s[0]][s[1]]
                            max_p = -1
                            max_b = None
                            for b in percentages_selected:

                                if b not in processed_data[StatDictKeys.FINAL_KEY][cm][g][s[0]][new_stat]:
                                    processed_data[StatDictKeys.FINAL_KEY][cm][g][s[0]][new_stat][b] = 0

                                p = percentages_selected[b]
                                if p > max_p:
                                    max_p = p 
                                    max_b = b 
                            
                            processed_data[StatDictKeys.FINAL_KEY][cm][g][s[0]][new_stat][max_b] += 1

                    elif type(s) != list:
                        #iterate through all the keys to collect the distribution info
                        new_stat = Stats.FINAL_STAT_DIST + " ~ " + s
                        if new_stat not in processed_data[StatDictKeys.FINAL_KEY][cm][g]:
                            processed_data[StatDictKeys.FINAL_KEY][cm][g][new_stat] = []

                        for key in keys:
                            processed_data[StatDictKeys.FINAL_KEY][cm][g][new_stat].append(processed_data[key][cm][g][s])



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
    
    def get_pair_scores(self, num_rounds_per_game, red_words_flipped_by_round, \
        blue_words_flipped_by_round, bystander_words_flipped_by_round, assassin_words_flipped_by_round):
        
        #A dictionary that keeps thrack of all the events we've seen up until now
        events = {}

        #Generate all of the events that are possible
        pos_events = self.generate_pos_events()

        #Put those counts in a dictionary
        for e in pos_events:
            events[e] = 0
        
        #Create an arry to keep all of the pair scores for every game
        pair_scores = []

        #load the model
        model = utils.load_colt_model()

        event_arrays = self.get_event_arrays(num_rounds_per_game, red_words_flipped_by_round, \
            blue_words_flipped_by_round, bystander_words_flipped_by_round, assassin_words_flipped_by_round)


        for g in event_arrays:
            for round_outcome in g:
                e = self.create_string(round_outcome)
                events[e] += 1
            vec = self.get_feature_vec(events, pos_events)
            pair_scores.append(model.predict(np.array(vec).reshape(1, -1))[0])

        return pair_scores

    def create_string(self, arr):
        res = ''
        for num in arr:
            res += str(num)
        return res
    
    def generate_pos_events(self):
        res = []
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
                res.append(self.create_string(key))
        return res

    def get_feature_vec(self, occurance_dict, pos_events):
        x = []
        total_events = sum(occurance_dict.values())
        for e in pos_events:
            if total_events != 0:
                x.append(occurance_dict[e] / total_events)
            else:
                x.append(0)
        return x

    def get_event_arrays(self, num_rounds_per_game, red_words_flipped_by_round, \
        blue_words_flipped_by_round, bystander_words_flipped_by_round, assassin_words_flipped_by_round):
        event_arrays = []

        curr_ind = 0
        for i in range(len(num_rounds_per_game)):
            event_arrays.append([])
            for j in range(curr_ind, curr_ind + int(num_rounds_per_game[i])):
                rwf = red_words_flipped_by_round[j]
                bwf = blue_words_flipped_by_round[j]
                bywf = bystander_words_flipped_by_round[j]
                awf = assassin_words_flipped_by_round[j]

                event_arrays[i].append([rwf, bwf, bywf, awf])

            curr_ind += int(num_rounds_per_game[i])
        
        return event_arrays
    
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

    def calculate_arm_weights_by_game(self, parsed_data, lp, cm, g, key):
        round_arm_weights = parsed_data[lp][cm][g][key][Stats.ARM_WEIGHTS_BY_ROUND]
        game_arm_weights = {}
        curr_pos = 0

        #Get the initial value
        for bot in round_arm_weights:
            game_arm_weights[bot] = []
            #Now add the last of each game to the list
            game_arm_weights[bot].append(round_arm_weights[bot][curr_pos])

        for rounds_in_game in parsed_data[lp][cm][g][Stats.NUM_ROUNDS_PER_GAME]:
            #Set the new position so we can add the correct corresponding arm weights
            curr_pos += rounds_in_game
            #loop through all of the arms
            for bot in round_arm_weights:
                # Now add the last of each game to the list
                # Subtract 1 because the arm weights are added before each round
                try:
                    game_arm_weights[bot].append(round_arm_weights[bot][curr_pos - 1])
                except Exception as e:
                    pass
                    print("[ERROR] -", "cm: ", cm, "\ng: ", g)
        
        return game_arm_weights
    
    def get_running_averages(self, processed_data, parsed_data, lp, cm, g):
        # Stats, StatDictKeys
        processed_data[lp][cm][g][Stats.RUNNING_AVG_WR] = self.calc_run_avg(parsed_data[lp][cm][g][Stats.GAME_WIN_LOSS])
        arr = [parsed_data[lp][cm][g][Stats.NUM_ROUNDS_PER_GAME][i] if parsed_data[lp][cm][g][Stats.GAME_WIN_LOSS][i] == 1 else 0 for i in range(len(parsed_data[lp][cm][g][Stats.NUM_ROUNDS_PER_GAME]))]
        processed_data[lp][cm][g][Stats.RUNNING_AVG_WT] = self.calc_run_avg_wt(arr)
        processed_data[lp][cm][g][Stats.RUNNING_AVG_RED_FLIP_BY_GAME] = self.calc_run_avg(processed_data[lp][cm][g][Stats.RED_FLIP_BY_GAME])
        processed_data[lp][cm][g][Stats.RUNNING_AVG_BLUE_FLIP_BY_GAME] = self.calc_run_avg(processed_data[lp][cm][g][Stats.BLUE_FLIP_BY_GAME])
        processed_data[lp][cm][g][Stats.RUNNING_AVG_BYSTANDER_FLIP_BY_GAME] = self.calc_run_avg(processed_data[lp][cm][g][Stats.BYSTANDER_FLIP_BY_GAME])
        processed_data[lp][cm][g][Stats.RUNNING_AVG_ASSASSIN_FLIP_BY_GAME] = self.calc_run_avg(processed_data[lp][cm][g][Stats.ASSASSIN_FLIP_BY_GAME])

    def calc_run_avg_wt(self, arr):
        running_averages = []
        curr_sum = 0
        curr_count = 0
        for e in arr:
            if e == 0:
                if len(running_averages) > 0:
                    running_averages.append(running_averages[-1])
                else:
                    running_averages.append(0)
                continue #we don't count it
            curr_sum += e
            curr_count += 1
            running_averages.append(curr_sum / curr_count)
        return running_averages
    
    def calc_run_avg(self, arr):
        curr_sum = 0
        curr_count = 0
        new_arr = []
        for e in arr:
            curr_sum += e 
            curr_count += 1 
            new_arr.append(curr_sum / curr_count)
        return new_arr
    
    def calc_bot_score_sliding_window(self, data):
        sliding_wind_avgs = []

        event_arrays = self.get_event_arrays(data[Stats.NUM_ROUNDS_PER_GAME], \
                        data[Stats.RED_WORDS_FLIPPED_BY_ROUND], data[Stats.BLUE_WORDS_FLIPPED_BY_ROUND], \
                        data[Stats.BYSTANDER_WORDS_FLIPPED_BY_ROUND], data[Stats.ASSASSIN_WORDS_FLIPPED_BY_ROUND])

        #Generate all of the events that are possible
        pos_events = self.generate_pos_events()

        #load the model
        model = utils.load_colt_model() 

        for i in range(len(event_arrays)):
            #A dictionary that keeps thrack of all the events we've seen up until now
            events = {}

            #Put those counts in a dictionary
            for e in pos_events:
                events[e] = 0

            for g in event_arrays[i:]:
                for round_outcome in g:
                    e = self.create_string(round_outcome)
                    events[e] += 1

            vec = self.get_feature_vec(events, pos_events)
            sliding_wind_avgs.append(model.predict(np.array(vec).reshape(1, -1))[0])
        
        return sliding_wind_avgs

    
    def calc_sliding_window_averages(self, data):
        sliding_wind_avgs = []
        for i in range(len(data)):
            sliding_wind_avgs.append(np.mean(data[i:]))
        return sliding_wind_avgs
    
    def calc_sliding_window_average_wt(self, data):
        sliding_wind_avgs = []
        # at any values of zero, I just need to put whatever the mean is 
        for i in range(len(data)):
            curr_window = self.calc_run_avg_wt(data[i:])
            if len(curr_window) > 0:
                sliding_wind_avgs.append(curr_window[-1])
            else:
                sliding_wind_avgs.append(sliding_wind_avgs[-1])
        return sliding_wind_avgs


    def get_sliding_window_averages(self, processed_data, parsed_data, lp, cm, g):
        processed_data[lp][cm][g][Stats.SLIDING_WINDOW_PAIR_SCORES] = self.calc_bot_score_sliding_window(parsed_data[lp][cm][g])
        processed_data[lp][cm][g][Stats.SLIDING_WINDOW_AVG_WR] = self.calc_sliding_window_averages(parsed_data[lp][cm][g][Stats.GAME_WIN_LOSS])
        arr = [parsed_data[lp][cm][g][Stats.NUM_ROUNDS_PER_GAME][i] if parsed_data[lp][cm][g][Stats.GAME_WIN_LOSS][i] == 1 else 0 for i in range(len(parsed_data[lp][cm][g][Stats.NUM_ROUNDS_PER_GAME]))]
        processed_data[lp][cm][g][Stats.SLIDING_WINDOW_AVG_WT] = self.calc_sliding_window_average_wt(arr)
        processed_data[lp][cm][g][Stats.SLIDING_WINDOW_AVG_RED_FLIP_BY_GAME] = self.calc_sliding_window_averages(processed_data[lp][cm][g][Stats.RED_FLIP_BY_GAME])
        processed_data[lp][cm][g][Stats.SLIDING_WINDOW_AVG_BLUE_FLIP_BY_GAME] = self.calc_sliding_window_averages(processed_data[lp][cm][g][Stats.BLUE_FLIP_BY_GAME])
        processed_data[lp][cm][g][Stats.SLIDING_WINDOW_AVG_BYSTANDER_FLIP_BY_GAME] = self.calc_sliding_window_averages(processed_data[lp][cm][g][Stats.BYSTANDER_FLIP_BY_GAME])
        processed_data[lp][cm][g][Stats.SLIDING_WINDOW_AVG_ASSASSIN_FLIP_BY_GAME] = self.calc_sliding_window_averages(processed_data[lp][cm][g][Stats.ASSASSIN_FLIP_BY_GAME])

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

    def get_mean_w_moe(self, arr):
            mean = np.mean(arr) 
            n = len(arr)
            std_error = stats.sem(arr)
            #we use the t distribution to account for non-normal distributions
            t = stats.t.ppf((1 + self.confidence_level) / 2, n-1)
            margin_of_error = t * std_error 

            return mean, margin_of_error
    
    def get_averages_singles(self, averaged_data, processed_data, lps, key, cm, g):
        arr = []
        for lp in lps:
            arr.append(processed_data[lp][cm][g][key])

        averaged_data[cm][g][key] = self.get_mean_w_moe(arr)
    
    def get_averages_lists(self, averaged_data, processed_data, lps, key, cm, g):
        final_arr = []
        #We can assume all of the lists are the same size
        for i in range(len(processed_data[lps[0]][cm][g][key])):
            temp_arr= []
            for lp in lps:
                temp_arr.append(processed_data[lp][cm][g][key][i])

            final_arr.append(np.mean(temp_arr))
        averaged_data[cm][g][key] = final_arr

    
    def get_averages_dict_single(self, averaged_data, processed_data, lps, dict_key, stat_key, cm, g):
        if dict_key not in processed_data[lps[0]][cm][g]:
            return 
        val_dict = {}
        for lp in lps:
            try:
                for arm in processed_data[lp][cm][g][dict_key][stat_key]:
                    if arm not in val_dict:
                        val_dict[arm] = []
                    val_dict[arm].append(processed_data[lp][cm][g][dict_key][stat_key][arm])
            except:
                continue
        #Now loop back through the arms and take the average of the list
        for arm in val_dict:
            val_dict[arm] = np.average(val_dict[arm])

        if dict_key not in averaged_data[cm][g]:
            averaged_data[cm][g][dict_key] = {}

        averaged_data[cm][g][dict_key][stat_key] = val_dict

    def get_averages_dict_lists(self, averaged_data, processed_data, lps, dict_key, stat_key, cm, g):
        if dict_key not in processed_data[lps[0]][cm][g]:
            return 
        final_val_dict = {}
        #loop through all of the games
        for i in range(len(processed_data[lps[0]][cm][g][dict_key][stat_key][list(processed_data[lps[0]][cm][g][dict_key][stat_key].keys())[0]])):
            temp_val_dict = {}
            for lp in lps:
                try:
                    for arm in processed_data[lp][cm][g][dict_key][stat_key]:
                        if arm not in temp_val_dict:
                            temp_val_dict[arm] = []
                        temp_val_dict[arm].append(processed_data[lp][cm][g][dict_key][stat_key][arm][i])
                except:
                    continue
            for arm in temp_val_dict:
                if arm not in final_val_dict:
                    final_val_dict[arm] = []
                final_val_dict[arm].append(np.average(temp_val_dict[arm]))
        

        if dict_key not in averaged_data[cm][g]:
            averaged_data[cm][g][dict_key] = {}

        averaged_data[cm][g][dict_key][stat_key] = final_val_dict

    
    def get_averages(self, processed_data):
        averaged_data = {}

        lps = list(processed_data.keys())
        t = lps[0]
        for cm in processed_data[t]:
            if cm not in averaged_data:
                averaged_data[cm] = {}
            for g in processed_data[t][cm]:
                if g not in averaged_data[cm]:
                    averaged_data[cm][g] = {}
                #Now we loop through all of the lps to get averages for the stats
                #TODO: consider calculating confidence intervals as well

                #Average the win rates
                self.get_averages_singles(averaged_data, processed_data, lps, Stats.WIN_RATE, cm, g)

                #Average the win times
                self.get_averages_singles(averaged_data, processed_data, lps, Stats.AVG_WIN_TIME, cm, g)

                #Average the min win timest
                self.get_averages_singles(averaged_data, processed_data, lps, Stats.MIN_WIN_TIME, cm, g)

                #Average the pair scores
                #TODO: Find a way to get these averages with differing length lists!!! np.nanmean()
                self.get_averages_lists(averaged_data, processed_data, lps, Stats.PAIR_SCORES, cm, g)

                #Average the final pair scores
                self.get_averages_singles(averaged_data, processed_data, lps, Stats.FINAL_PAIR_SCORE, cm, g)

                #Average the avg red/blue/bystander/assassin words flipped by game
                self.get_averages_singles(averaged_data, processed_data, lps, Stats.AVG_RED_FLIP_BY_GAME, cm, g)
                self.get_averages_singles(averaged_data, processed_data, lps, Stats.AVG_BLUE_FLIP_BY_GAME, cm, g)
                self.get_averages_singles(averaged_data, processed_data, lps, Stats.AVG_BYSTANDER_FLIP_BY_GAME, cm, g)
                self.get_averages_singles(averaged_data, processed_data, lps, Stats.AVG_ASSASSIN_FLIP_BY_GAME, cm, g)

                #average the red/blue/bystander/assassin words flipped by game
                self.get_averages_lists(averaged_data, processed_data, lps, Stats.RED_FLIP_BY_GAME, cm, g)
                self.get_averages_lists(averaged_data, processed_data, lps, Stats.BLUE_FLIP_BY_GAME, cm, g)
                self.get_averages_lists(averaged_data, processed_data, lps, Stats.BYSTANDER_FLIP_BY_GAME, cm, g)
                self.get_averages_lists(averaged_data, processed_data, lps, Stats.ASSASSIN_FLIP_BY_GAME, cm, g)

                #average running totals
                self.get_averages_lists(averaged_data, processed_data, lps, Stats.RUNNING_AVG_WR, cm, g)
                self.get_averages_lists(averaged_data, processed_data, lps, Stats.RUNNING_AVG_WT, cm, g)
                self.get_averages_lists(averaged_data, processed_data, lps, Stats.RUNNING_AVG_RED_FLIP_BY_GAME, cm, g)
                self.get_averages_lists(averaged_data, processed_data, lps, Stats.RUNNING_AVG_BLUE_FLIP_BY_GAME, cm, g)
                self.get_averages_lists(averaged_data, processed_data, lps, Stats.RUNNING_AVG_BYSTANDER_FLIP_BY_GAME, cm, g)
                self.get_averages_lists(averaged_data, processed_data, lps, Stats.RUNNING_AVG_ASSASSIN_FLIP_BY_GAME, cm, g)

                #average sliding windows
                self.get_averages_lists(averaged_data, processed_data, lps, Stats.SLIDING_WINDOW_PAIR_SCORES, cm, g)
                self.get_averages_lists(averaged_data, processed_data, lps, Stats.SLIDING_WINDOW_AVG_WR, cm, g)
                self.get_averages_lists(averaged_data, processed_data, lps, Stats.SLIDING_WINDOW_AVG_WT, cm, g)
                self.get_averages_lists(averaged_data, processed_data, lps, Stats.SLIDING_WINDOW_AVG_RED_FLIP_BY_GAME, cm, g)
                self.get_averages_lists(averaged_data, processed_data, lps, Stats.SLIDING_WINDOW_AVG_BLUE_FLIP_BY_GAME, cm, g)
                self.get_averages_lists(averaged_data, processed_data, lps, Stats.SLIDING_WINDOW_AVG_BYSTANDER_FLIP_BY_GAME, cm, g)
                self.get_averages_lists(averaged_data, processed_data, lps, Stats.SLIDING_WINDOW_AVG_ASSASSIN_FLIP_BY_GAME, cm, g)

                #Take care of learn log stats
                #Check that if it's a learning experiment, if there is a cm ensemble
                if len(self.experiment_paths.learn_log_filepaths_cm) > 0:
                    #average percentage bots chosen
                    self.get_averages_dict_single(averaged_data, processed_data, lps, StatDictKeys.CM_LEARN_STATS, Stats.PERCENTAGE_BOT_CHOSEN, cm, g)
                    #average arm weights
                    self.get_averages_dict_lists(averaged_data, processed_data, lps, StatDictKeys.CM_LEARN_STATS, Stats.ARM_WEIGHTS_BY_GAME, cm, g)

                if len(self.experiment_paths.learn_log_filepaths_g) > 0:
                    #average percentage bots chosen
                    self.get_averages_dict_single(averaged_data, processed_data, lps, StatDictKeys.G_LEARN_STATS, Stats.PERCENTAGE_BOT_CHOSEN, cm, g)
                    #average arm weights
                    self.get_averages_dict_lists(averaged_data, processed_data, lps, StatDictKeys.G_LEARN_STATS, Stats.ARM_WEIGHTS_BY_GAME, cm, g)

        return averaged_data