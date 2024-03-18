'''
This file creates files based off of the input hyper parameters. It acts like a hashing function by creating the same file name when the same hyperparameters are selected
but all of the names are unique with each change in a hyperparameter. 
This allows us to keep experiments separate and identifiable. 
This file is also in charge of deleting files that already exist when an experiment is run again. (we might re-run experiments for bug fixes and what not)
It loads the needed filepaths into the file_paths_obj and opens the needed files  and holds/opens/closes the actual file objects
'''

from os.path import join
from play_games.utils.analysis_files.analysis_utils import PERFORMANCE_PROGRESSION_STATS, PERFORMANCE_PROGRESSION_SLIDING_WINDOW_STATS, MAIN_STATS_KEYS

from play_games.bots.types import AIType
from play_games.bots.types.bot_to_ai import get_ai
from play_games.paths.creator.file_name_directory_elements import FileNameDirectoryElements as name_elements
from ._base import ExperimentPathCreator
from .__tools import create_round_logs_files

class LearningExperimentPathCreator(ExperimentPathCreator):
    
    def get_experiment_description(self):
        prefix = name_elements.WITH_LM if self.experiment_settings.include_same_lm else name_elements.WITHOUT_LM
        return f"{prefix}{self.experiment_settings.ensemble_parameters}{name_elements.LEARN_PERIOD_ITERATIONS_PREFIX}"
    
    def get_root_dir_extension(self):
        return name_elements.LEARNING_EXPERIMENTS_DIR

    def create_directories(self, root_dir):
        self._create_learning_figure_directories(root_dir)
        
        self.experiment_paths.learn_period_analyses_dir_path = join(root_dir, name_elements.LEARN_PERIOD_ANALYSES_DIR)
        self.experiment_paths.learn_experiment_analyses_dir_path = join(root_dir, name_elements.LEARN_EXPERIMENT_ANALYSES_DIR)
        
        self.experiment_paths.learn_logs_dir_path = join(root_dir, name_elements.RAW_DATA_DIR, name_elements.LEARN_LOGS_DIR)
        self.experiment_paths.learn_tables_dir_path = join(root_dir, name_elements.VISUALIZATIONS_DIR, name_elements.TABLES_DIR, name_elements.LEARN_TABLES_DIR)
    
    def _create_learning_figure_directories(self, root_dir):
        learn_figs_dir = join(root_dir, name_elements.VISUALIZATIONS_DIR, name_elements.FIGURES_DIR, name_elements.LEARN_FIGS_DIR)
        self.experiment_paths.learn_figs_dir_path = learn_figs_dir
        self.experiment_paths.performance_progression_dir_path = join(learn_figs_dir, name_elements.PERF_PROG_DIR)
        self.experiment_paths.performance_progression_sliding_window_dir_path = join(learn_figs_dir, name_elements.PERF_PROG_SLIDE_WIND_DIR)
        self.experiment_paths.arm_weights_dir_path = join(learn_figs_dir, name_elements.ARM_WEIGHTS_DIR)
        self.experiment_paths.percent_selected_dir_path = join(learn_figs_dir, name_elements.PERC_SELECTED_DIR)  
        self.experiment_paths.final_stat_distribution_dir_path = join(learn_figs_dir, name_elements.FINAL_STAT_DIST_DIR)

    def create_file_paths(self, filename_prefix):
        contains_ensemble_cm = self._do_spymasters_contain_ensemble()
        contains_ensemble_g = self._do_guessers_contain_ensemble

        #If there are ensemble bots then we need to instantiate those filepaths
        name = filename_prefix

        lower, upper = self.experiment_settings.iteration_range

        #We take care of naming the files that summarize the individual ones
        itr_range = f"{lower}-{upper}"

        #learning experiment
        if contains_ensemble_cm:
            #learn experiment file names
            #directory information has already been appended here
            dir = self.experiment_paths.learn_experiment_analyses_dir_path
            this_name = "{}{}{}{}{}".format(
                name_elements.LEARN_EXPERIMENT_ANALYSIS_PREFIX,
                name_elements.SPYMASTER_PREFIX,
                name,
                itr_range,
                name_elements.LEARN_EXPERIMENT_ANALYSIS_FILE_TYPE
            )
            self.experiment_paths.learn_experiment_analysis_filepath_cm = join(dir, this_name)
            
        if contains_ensemble_g:
            dir = self.experiment_paths.learn_experiment_analyses_dir_path
            this_name = "{}{}{}{}{}".format(
                name_elements.LEARN_EXPERIMENT_ANALYSIS_PREFIX,
                name_elements.GUESSER_PREFIX,
                name,
                itr_range,
                name_elements.LEARN_EXPERIMENT_ANALYSIS_FILE_TYPE
            )
            self.experiment_paths.learn_experiment_analysis_filepath_g = join(dir, this_name)

        #name experiment specific supporting files here
        #Don't worry about naming figure files yet becuase those are just intermediary
        #add names to an array so that we can do the naming of the files that all experiment types have together
        for i in range(lower, upper):
            #We take care of naming the individual iteration files

            if contains_ensemble_cm:
                self._create_learn_log_paths(name_elements.SPYMASTER_PREFIX, name, i, self.experiment_paths.learn_log_filepaths_cm)
                self._create_learn_table_paths(name_elements.SPYMASTER_PREFIX, name, i)
                self._create_learn_fig_paths(name, name_elements.SPYMASTER_PREFIX, i)

            if contains_ensemble_g:
                self._create_learn_log_paths(name_elements.GUESSER_PREFIX, name, i, self.experiment_paths.learn_log_filepaths_g)
                self._create_learn_table_paths(name_elements.GUESSER_PREFIX, name, i)
                self._create_learn_fig_paths(name, name_elements.GUESSER_PREFIX, i)
                    
            create_round_logs_files(self.experiment_paths, name, i)
        
        #We add one more processed data file and learn table file because we will be combining all of the components 
        #We do this only for learning experiments because it is the only type of experiment that needs 
        #averages across many tournaments
        dir = self.experiment_paths.processed_data_dir_path
        this_name = f"{name_elements.PROCESSED_DATA_PREFIX}{name}_final{name_elements.PROCESSED_DATA_FILE_TYPE}"
        self.experiment_paths.processed_data_filepaths.append(join(dir, this_name))

        self._create_learn_table_paths("", filename_prefix, "final")


        #Create learning figures for the final (averaged) data
        if contains_ensemble_cm:
            self._create_learn_fig_paths(name, name_elements.SPYMASTER_PREFIX, "_final")
        if contains_ensemble_g:
            self._create_learn_fig_paths(name, name_elements.GUESSER_PREFIX, "_final")

    
    def _create_learn_log_paths(self, role_prefix, filename_prefix, iteration, paths):

        dir = self.experiment_paths.learn_logs_dir_path
        this_name = f"{name_elements.LEARN_LOG_PREFIX}{role_prefix}{filename_prefix}_{iteration}{name_elements.LEARN_LOG_FILE_TYPE}"
        paths.append(join(dir, this_name))

    def _create_learn_table_paths(self, role_prefix, filename_prefix, iteration):
        dir = self.experiment_paths.learn_tables_dir_path
        this_name = f"{name_elements.LEARN_TABLE_PREFIX}{role_prefix}{filename_prefix}_{iteration}{name_elements.LEARN_TABLE_FILE_TYPE}"
        self.experiment_paths.learn_table_filepaths.append(join(dir, this_name))

    def _create_learn_fig_paths(self, name, type_prefix, itr_suffix):
        b_type = type_prefix[:-1]

        #set the type prefix in all of the filepath dictionaries
        if b_type not in self.experiment_paths.performance_progression_filepaths:
            self.experiment_paths.performance_progression_filepaths[b_type] = {}
            self.experiment_paths.performance_progression_sliding_window_filepaths[b_type] = {}
        

        if b_type not in self.experiment_paths.percent_selected_filepaths:
            #arm percentage figures
            dir = self.experiment_paths.percent_selected_dir_path
            this_name = f"{name_elements.ARM_PERCENTAGE_PREFIX}{type_prefix}{name}{itr_suffix}"
            self.experiment_paths.percent_selected_filepaths[b_type] = join(dir, this_name)
        
        if b_type not in self.experiment_paths.arm_weights_filepaths:
            #arm weights figures
            dir = self.experiment_paths.arm_weights_dir_path
            this_name = f"{name_elements.ARM_WEIGHTS_PREFIX}{type_prefix}{name}{itr_suffix}"
            self.experiment_paths.arm_weights_filepaths[b_type] = join(dir, this_name)
        
        if b_type not in self.experiment_paths.final_stat_distribution_filepaths:
            dir = self.experiment_paths.final_stat_distribution_dir_path
            this_name = f"{name_elements.FINAL_STAT_DIST_PREFIX}{type_prefix}{name}{itr_suffix}"
            self.experiment_paths.final_stat_distribution_filepaths[b_type] = join(dir, this_name)

        #performance progression figures (loop through all of the wanted stats for this)
        for stat in PERFORMANCE_PROGRESSION_STATS:
            if stat not in self.experiment_paths.performance_progression_filepaths[b_type]:
                self.experiment_paths.performance_progression_filepaths[b_type][stat] = []
            dir = join(self.experiment_paths.performance_progression_dir_path, stat)
            this_name = f"{name_elements.PERFORMANCE_PROGRESSION_PREFIX}{b_type}_{stat}_{name}{itr_suffix}"
            self.experiment_paths.performance_progression_filepaths[b_type][stat].append(join(dir, this_name))
        
        for stat in PERFORMANCE_PROGRESSION_SLIDING_WINDOW_STATS:
            if stat not in self.experiment_paths.performance_progression_sliding_window_filepaths[b_type]:
                self.experiment_paths.performance_progression_sliding_window_filepaths[b_type][stat] = []
            dir = join(self.experiment_paths.performance_progression_sliding_window_dir_path, stat)
            this_name = name_elements.PERFORMANCE_PROGRESSION_SLIDING_WINDOW_PREFIX + b_type + "_" + stat + "_" + name + str(itr_suffix)
            self.experiment_paths.performance_progression_sliding_window_filepaths[b_type][stat].append(join(dir, this_name))

    def _do_spymasters_contain_ensemble(self):
        cm_ai_types = set(map(get_ai, self.experiment_settings.spymasters))        
        return AIType.DISTANCE_ENSEMBLE in cm_ai_types
    
    def _do_guessers_contain_ensemble(self):
        g_ai_types = set(map(get_ai, self.experiment_settings.guessers))
        return AIType.DISTANCE_ENSEMBLE in g_ai_types