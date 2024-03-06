import copy
from tabulate import tabulate
import numpy as np
from play_games.bots.types.bot_to_lm import get_lm

from play_games.utils.utils import create_path
from play_games.utils.analysis_files.analysis_utils import StatDictKeys, MAIN_STATS_KEYS, extract_val, find_ensemble, find_rand_bot, is_ensemble, is_rand_ensemble

class TableCreator:
    def __init__(self, experiment_settings):
        self.precision = 4
        self.experiment_settings = experiment_settings 

    def create_learn_table(self, processed_data, fp, solo_bot_data, performance_stats, has_ensemble_cm, has_ensemble_g):

        #if there is an ensemble cm, include avg cm performance, best cm for g (not including ensemble), best avg cm, and avg cm performance (in the columns)
        #if there ins an ensemble g, include avg g performance, best g for cm (not including ensemble), best avg g, and avg g performance (in the rows)
        #add needed columns/rows for type of ensemble bots included

        tables = {}
        for stat in MAIN_STATS_KEYS:
            tables[stat] = self.assemble_learn_table(processed_data, solo_bot_data, performance_stats, stat, has_ensemble_cm, \
                has_ensemble_g)

        #We start with adding the 
        #Save table
        #open file here and pass it into the function 
        create_path(fp)
        with open(fp, "w+", encoding="utf8") as f:
            self.save_tables(tables, f)

    def assemble_learn_table(self, processed_data, solo_bot_data, performance_stats, stat, has_ensemble_cm, has_ensemble_g):

        table = self.assemble_main_table(solo_bot_data, stat, has_ensemble_cm, has_ensemble_g)

        #add in other stuff
        self.merge_with_performance_stats(table, processed_data, performance_stats, stat, has_ensemble_cm, has_ensemble_g)
        # self.merge_with_processed_data(table, processed_data, stat, has_ensemble_cm, has_ensemble_g)

        return table

    def assemble_main_table(self, processed_data, stat, has_ensemble_cm, has_ensemble_g):
        #loop throught the cms and then loop through the gs
        table = []

        codemasters = list(processed_data.keys())
        guessers = list(processed_data[codemasters[0]].keys())

        #sort them to ensure that the bots line up correctly 
        codemasters = sorted(codemasters, reverse=True)
        guessers = sorted(guessers, reverse=True)

        headers = copy.deepcopy(guessers)
        headers.insert(0, "cm/g")

        for i in range(len(codemasters)):
            table.append([codemasters[i]])
            for j in range(len(guessers)):
                if self.experiment_settings.include_same_lm or (get_lm(codemasters[i]) != get_lm(guessers[j])):
                    table[i].append(self.round_val(extract_val(processed_data[codemasters[i]][guessers[j]][stat])))
                else:
                    table[i].append('-')

        table.insert(0, headers)

        self.add_main_avgs(table, has_ensemble_cm, has_ensemble_g)
                
        #meanwhile 
        return table

    def add_main_avgs(self, table, has_ensemble_cm, has_ensemble_g):
        if has_ensemble_cm:
            #then we add a new col with avgs across rows 
            cm_avgs = []
            for i in range(1, len(table)):
                vals = [table[i][j] for j in range(len(table[i])) if type(table[i][j]) == float]
                cm_avgs.append(self.round_val(np.mean(vals)))
        if has_ensemble_g:
            #then we add a new row with avgs across columns
            g_avgs = []
            for i in range(1, len(table[0])):
                vals = [table[j][i] for j in range(1, len(table)) if type(table[j][i]) == float]
                g_avgs.append(self.round_val(np.mean(vals)))
        
        if has_ensemble_cm:
            table.append([StatDictKeys.AVG_PERF] + cm_avgs)
        if has_ensemble_g:
            table[0].append(StatDictKeys.AVG_PERF)
            for i in range(1, len(g_avgs) + 1):
                table[i].append(g_avgs[i - 1])
        if has_ensemble_cm and has_ensemble_g:
            #add the averages of the average
            table[-1].append(self.round_val(np.mean(cm_avgs)))

    def merge_with_performance_stats(self, table, processed_data, performance_stats, stat, has_ensemble_cm, has_ensemble_g):
        #add the needed columns
        #if ensemble g or cm, then add Best overall, Best Avg, and Rand for along col or row respctively

        self.add_best_overall_vals(table, performance_stats, stat, has_ensemble_cm, has_ensemble_g)
        self.add_best_avg_vals(table, performance_stats, stat, has_ensemble_cm, has_ensemble_g)
        self.add_random_vals(table, processed_data, performance_stats, stat, has_ensemble_cm, has_ensemble_g)

    def add_performance_vals(self, key, num_ext, table, performance_stats, stat, has_ensemble_cm, has_ensemble_g):
        if has_ensemble_cm:
            #We add overall to a row
            values = [v for v in performance_stats[StatDictKeys.CODEMASTER][stat][key] if (not is_rand_ensemble(v[1])) and (not is_ensemble(v[1]))]
            values = [self.round_val(e[-1]) for e in values]
            values.append(self.round_val(np.mean(values)))
            table.append([key] + values)

        if has_ensemble_g:
            #we start by adding best overall info to a new column
            table[0].append(key)
            values = [v for v in performance_stats[StatDictKeys.GUESSER][stat][key] if (not is_rand_ensemble(v[0])) and (not is_ensemble(v[0]))]
            values = [self.round_val(e[-1]) for e in values]
            values.append(self.round_val(np.mean(values)))
            for i in range(1, len(values) + 1):
                table[i].append(self.round_val(values[i - 1]))
        
        #Now we add extra hyphens as needed
        #if there are both ensembles, we add extras, otherwise we don't need to worry about it 
        if has_ensemble_cm and has_ensemble_g:
            for i in range(num_ext):
                #add to the final row
                table[-1].append('-')
                #add to the final column
                table[-2 - i].append('-')

            #we need to add one in the corner as well
            table[-1].append('-')

    def add_best_overall_vals(self, table, performance_stats, stat, has_ensemble_cm, has_ensemble_g):

        self.add_performance_vals(StatDictKeys.BEST_OVERALL, 0, table, performance_stats, stat, has_ensemble_cm, has_ensemble_g)
    
    def add_best_avg_vals(self, table, performance_stats, stat, has_ensemble_cm, has_ensemble_g):

        self.add_performance_vals(StatDictKeys.BEST_AVG, 1, table, performance_stats, stat, has_ensemble_cm, has_ensemble_g)

    def add_random_vals(self, table, processed_data, performance_stats, stat, has_ensemble_cm, has_ensemble_g):

        self.add_performance_vals(StatDictKeys.RANDOM, 2, table, performance_stats, stat, has_ensemble_cm, has_ensemble_g)

        #Now we add the random v random score to the bottom corner
        rand_cm = find_rand_bot(processed_data.keys())
        rand_g = find_rand_bot(processed_data[list(processed_data.keys())[0]])

        if has_ensemble_cm and has_ensemble_g and rand_cm != None and rand_g != None:
            table[-1][-1] = self.round_val(extract_val(processed_data[rand_cm][rand_g][stat]))


    def merge_with_processed_data(self, table, processed_data, stat, has_ensemble_cm, has_ensemble_g):
        #we need to find the ensemble bots 
        ensemble_cm = find_ensemble(processed_data.keys())
        if has_ensemble_cm and ensemble_cm != None:

            rand_g = find_rand_bot(processed_data[ensemble_cm].keys())

            ensemble_cm_vals = []
            for g in processed_data[ensemble_cm]:
                if g != rand_g and not is_ensemble(g):
                    ensemble_cm_vals.append(extract_val(processed_data[ensemble_cm][g][stat]))

            #add average performance 
            ensemble_cm_vals.append(self.round_val(np.mean(ensemble_cm_vals)))

            #if there is an ensemble g, then we add 2 '-'
            if has_ensemble_g:
                ensemble_cm_vals.extend(['-', '-'])

            #add the performance with random 
            if rand_g != None:
                ensemble_cm_vals.append(self.round_val(extract_val(processed_data[ensemble_cm][rand_g][stat])))
            else:
                ensemble_cm_vals.append('-')
            
            #Now we add the row
            table.append([ensemble_cm] + ensemble_cm_vals)

        ensemble_g = find_ensemble(processed_data[list(processed_data.keys())[0]].keys())
        if has_ensemble_g and ensemble_g != None:
            rand_cm = find_rand_bot(processed_data.keys())

            ensemble_g_vals = []
            for cm in processed_data:
                if cm != rand_cm and not is_ensemble(cm):
                    ensemble_g_vals.append(extract_val(processed_data[cm][ensemble_g][stat]))

            #add average performance 
            ensemble_g_vals.append(self.round_val(np.mean(ensemble_g_vals)))

            #if there is an ensemble g, then we add 2 '-'
            if has_ensemble_cm:
                ensemble_g_vals.extend(['-', '-'])

            #add the performance with random 
            if rand_cm != None:
                ensemble_g_vals.append(self.round_val(extract_val(processed_data[rand_cm][ensemble_g][stat])))
            else:
                ensemble_g_vals.append('-')
            
            #Now we add the column 
            table[0].append(ensemble_g)
            for i, v in enumerate(ensemble_g_vals):
                table[i].append(v)
        
        #If there are both ensembles, we add their performance with each other 
        if has_ensemble_cm and has_ensemble_g and ensemble_cm != None and ensemble_g != None:
            table[-1][-1] = self.round_val(extract_val(processed_data[ensemble_cm][ensemble_g][stat]))
            

    def save_tables(self, tables, f):

        #loop through the stat tables and save each one to the opened file
        for stat in tables:
            f.write(stat + '\n')
            f.write(tabulate(tables[stat], headers='firstrow', stralign='center', tablefmt='fancy_grid', floatfmt='.4f') + '\n\n')
    
    def round_val(self, v):
        return round(v, self.precision)