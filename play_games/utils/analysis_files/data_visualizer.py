import numpy as np

from play_games.paths import file_paths
from play_games.utils.analysis_files.analysis_utils import DesiredStats, StatDictKeys, DesiredStatsKeys, MinMaxKeys, MAIN_STATS_KEYS, load_json, extract_val, find_rand_bot, is_ensemble
from play_games.utils.analysis_files.data_compiler import DataCompiler
from play_games.utils.analysis_files.figure_creator import FigureCreator
from play_games.utils.analysis_files.table_creator import TableCreator
from play_games.bots.types.bot_to_lm import get_lm
from play_games.configs.enums import ExperimentType

class DataVisualizer:

    def __init__(self, experiment_settings, experiment_paths):
        self.experiment_settings = experiment_settings
        self.learn_table_filepaths = experiment_paths.learn_table_filepaths
        self.desired_stats = DesiredStats()
        self.table_creator = TableCreator(experiment_settings)
        self.figure_creator = FigureCreator(experiment_settings, experiment_paths)
        self.data_compiler = DataCompiler(experiment_paths)

        self.compiled_data = {}
        self.figure_paths = {}

    def visualize_data(self, processed_data=None):
        #This is where we create the figures using our processed data

        #Check if this is a learning experiment
        if self.experiment_settings.experiment_type == ExperimentType.LEARNING_EXPERIMENT:

            lp = -1 #Later, this could be done for all lps if desired

            solo_bot_data = self.get_solo_bot_data()
            has_ensemble_cm, has_ensemble_g = self.get_ensemble_info(processed_data[StatDictKeys.FINAL_KEY])
            performance_stats = self.calculate_performance_stats(solo_bot_data, processed_data[StatDictKeys.FINAL_KEY], has_ensemble_cm, has_ensemble_g)

            self.table_creator.create_learn_table(processed_data[StatDictKeys.FINAL_KEY], self.learn_table_filepaths[lp], solo_bot_data, performance_stats, \
                                    has_ensemble_cm, has_ensemble_g)

            self.figure_creator.create_figures(processed_data[StatDictKeys.FINAL_KEY], lp, performance_stats)

            compiled_info = self.figure_creator.get_compiled_info(performance_stats, processed_data[StatDictKeys.FINAL_KEY])
            self.data_compiler.compile_data(compiled_info)

        elif self.experiment_settings.experiment_type == ExperimentType.PARAMETER_EXPERIMENT:
            self.figure_creator.create_param_vs_score_figures(processed_data[StatDictKeys.FINAL_KEY])
    

    def get_solo_bot_data(self):
        solo_bot_data = load_json(file_paths.dist_assoc_solitair_table_path)
        return solo_bot_data

    def get_ensemble_info(self, processed_data):
            #Create the base table for each stat
            #determine needed solitair bots (all of the codemasters and guessers that aren't ensembles)
            has_ensemble_cm = False 
            has_ensemble_g = False
            for cm in processed_data:
                if is_ensemble(cm):
                    has_ensemble_cm = True 
            
            for g in processed_data[list(processed_data.keys())[0]]:
                if is_ensemble(g):
                    has_ensemble_g = True

            return has_ensemble_cm, has_ensemble_g
        
    
    def calculate_performance_stats(self, solo_bot_data, processed_data, has_ensemble_cm, has_ensemble_g):
        #Now I need to calculate average performances, best avg performance, best overall performance for each stat

        performance_stats = {}

        for stat in MAIN_STATS_KEYS:

            if has_ensemble_cm:

                #Then I need to add the codemaster key to the dict
                if StatDictKeys.CODEMASTER not in performance_stats:
                    performance_stats[StatDictKeys.CODEMASTER] = {}
                
                performance_stats[StatDictKeys.CODEMASTER][stat] = {}

                #Caclulate average performances
                #I need all of the average cm performances accross guessers
                best_overall_cm_for_g = {}
                avg_vals = []

                # for every single cm
                for cm in solo_bot_data:
                    values = []

                    #get the values of every single guesser. 
                    # put the avg in avg_vals 
                    for g in solo_bot_data[cm]:

                        #We check to see if the two bots have the same underlying language models
                        if not self.experiment_settings.include_same_lm and \
                            get_lm(cm) == get_lm(g):
                            continue

                        values.append(extract_val(solo_bot_data[cm][g][stat]))


                        #We can also take care of finding the best overall cm for g
                        if g not in best_overall_cm_for_g:
                            best_overall_cm_for_g[g] = []
                        best_overall_cm_for_g[g].append((cm, extract_val(solo_bot_data[cm][g][stat])))


                    avg_v = np.mean(values)
                    avg_vals.append((cm, avg_v))


                self.sort_vals(avg_vals, stat)

                #Find best avg bot 
                best_avg_cm = avg_vals[0][0]
                best_avg_cm_vals = []
                best_overall_cm_for_g_vals = []

                for g in best_overall_cm_for_g:

                    #because we are already going through all the guessers, we put the values in the best avg vals array
                    if not self.experiment_settings.include_same_lm and get_lm(g) == get_lm(best_avg_cm):
                        #Then we need to find the second best avg cm
                        next_best_avg_cm = avg_vals[1][0]
                        #now we find it's value with this guesser 
                        best_avg_cm_vals.append((next_best_avg_cm, g, extract_val(solo_bot_data[next_best_avg_cm][g][stat])))
                    else:
                        best_avg_cm_vals.append((best_avg_cm, g, extract_val(solo_bot_data[best_avg_cm][g][stat])))

                    #because I already filtered out the similar language models in the list, I can just sort it and take the best
                    self.sort_vals(best_overall_cm_for_g[g], stat)
                    best_overall_cm_for_g_vals.append((best_overall_cm_for_g[g][0][0], g, best_overall_cm_for_g[g][0][1]))
                
                performance_stats[StatDictKeys.CODEMASTER][stat][StatDictKeys.BEST_AVG] = best_avg_cm_vals
                performance_stats[StatDictKeys.CODEMASTER][stat][StatDictKeys.BEST_OVERALL] = best_overall_cm_for_g_vals

            if has_ensemble_g:

                #Then I need to add the codemaster key to the dict
                if StatDictKeys.GUESSER not in performance_stats:
                    performance_stats[StatDictKeys.GUESSER] = {}
                performance_stats[StatDictKeys.GUESSER][stat] = {}

                #Caclulate average performances
                #I need all of the average cm performances accross guessers
                best_overall_g_for_cm = {}
                avg_vals = []

                # for every single cm
                for g in solo_bot_data[list(solo_bot_data.keys())[0]]:
                    values = []

                    #get the values of every single guesser. 
                    # put the avg in avg_vals 
                    for cm in solo_bot_data:

                        #We check to see if the two bots have the same underlying language models
                        if not self.experiment_settings.include_same_lm and get_lm(cm) == get_lm(g):
                            continue

                        values.append(extract_val(solo_bot_data[cm][g][stat]))


                        #We can also take care of finding the best overall cm for g
                        if cm not in best_overall_g_for_cm:
                            best_overall_g_for_cm[cm] = []
                        best_overall_g_for_cm[cm].append((g, extract_val(solo_bot_data[cm][g][stat])))


                    avg_v = np.mean(values)
                    avg_vals.append((g, avg_v))


                self.sort_vals(avg_vals, stat)

                #Find best avg bot 
                best_avg_g = avg_vals[0][0]
                best_avg_g_vals = []
                best_overall_g_for_cm_vals = []

                for cm in best_overall_g_for_cm:

                    #because we are already going through all the guessers, we put the values in the best avg vals array
                    if not self.experiment_settings.include_same_lm and get_lm(cm) == get_lm(best_avg_g):
                        #Then we need to find the second best avg cm
                        next_best_avg_g = avg_vals[1][0]
                        #now we find it's value with this guesser 
                        best_avg_g_vals.append((cm, next_best_avg_g, extract_val(solo_bot_data[cm][next_best_avg_g][stat])))
                    else:
                        best_avg_g_vals.append((cm, best_avg_g, extract_val(solo_bot_data[cm][best_avg_g][stat])))

                    #because I already filtered out the similar language models in the list, I can just sort it and take the best
                    self.sort_vals(best_overall_g_for_cm[cm], stat)
                    best_overall_g_for_cm_vals.append((cm, best_overall_g_for_cm[cm][0][0], best_overall_g_for_cm[cm][0][1]))
                
                performance_stats[StatDictKeys.GUESSER][stat][StatDictKeys.BEST_AVG] = best_avg_g_vals
                performance_stats[StatDictKeys.GUESSER][stat][StatDictKeys.BEST_OVERALL] = best_overall_g_for_cm_vals

        #now I can add the rand data
        self.add_rand_data(performance_stats, processed_data, has_ensemble_cm, has_ensemble_g)
            
        return performance_stats

    def add_rand_data(self, performance_stats, processed_data, has_ensemble_cm, has_ensemble_g):
        for stat in MAIN_STATS_KEYS:
            rand_cm = find_rand_bot(processed_data.keys())
            if has_ensemble_cm and rand_cm != None:
                rand_cm_data = []
                for g in processed_data[rand_cm]:
                    rand_cm_data.append((rand_cm, g, extract_val(processed_data[rand_cm][g][stat])))

                performance_stats[StatDictKeys.CODEMASTER][stat][StatDictKeys.RANDOM] = rand_cm_data

            rand_g = find_rand_bot(processed_data[list(processed_data.keys())[0]].keys())
            if has_ensemble_g and rand_g != None:
                rand_g_data = []
                for cm in processed_data:
                    rand_g_data.append((cm, rand_g, extract_val(processed_data[cm][rand_g][stat])))

                performance_stats[StatDictKeys.GUESSER][stat][StatDictKeys.RANDOM] = rand_g_data



    def sort_vals(self, vals, stat):
            if self.desired_stats.get_desired_stats(stat)[DesiredStatsKeys.OPTIMAL_EXTREME] == MinMaxKeys.MIN:
                #Then we sort lower to higher
                vals.sort(key=lambda x: x[1])
            else:
                vals.sort(key=lambda x: x[1], reverse=True) 
    


    


    


