import itertools
import os
from play_games.configs.enums import ExperimentType
from play_games.configs.experiment_settings import ExperimentSettings
from play_games.files.file_manager import FileManager
from play_games.utils.object_manager import ObjectManager
from play_games.paths import file_paths
from .run_games import RunGames
from play_games.utils import utils
from play_games.bots.types import AIType

#Pass in settings object to other files and set the needed parameters

class RunTournament:

    def __init__(self, object_manager: ObjectManager):
        self.exp_settings: ExperimentSettings = object_manager.experiment_settings
        self.file_manager: FileManager = object_manager.file_manager
        self.experiment_paths: file_paths.ExperimentPaths = object_manager.experiment_paths
        self.run_games = RunGames(object_manager)
        self.lower = 0 
        self.upper = 0 

    def run(self, iteration=0, parameter_index=0, seed=0):
        #Get needed information from the experiment_settings.py file
        is_learning_experiment = False
            
        if self.exp_settings.experiment_type == ExperimentType.PARAMETER_EXPERIMENT:
            fi = parameter_index
        else:
            fi = (iteration - self.lower)
       
        self.file_manager.open_round_file(fi)
        if self.experiment_paths.learn_log_filepaths_cm:
            self.file_manager.open_learn_cm_file(fi)
            is_learning_experiment = True

        if self.experiment_paths.learn_log_filepaths_g:
            self.file_manager.open_learn_g_file(fi)
            is_learning_experiment = True


        n = self.exp_settings.n_games 
        spymasters = self.exp_settings.spymasters
        guessers = self.exp_settings.guessers

        for b1, b2 in itertools.product(spymasters, guessers):
            #I need to check that at least one of the bots is ensemble if this is a learning experiment
                
            utils.cond_print(f'Simulating {n} games with {b1} and {b2}', self.exp_settings.verbose_flag)
            self.run_games.run_n_games(n, b1, b2, iteration, parameter_index, seed=seed)

        self.file_manager.close_round_file()
        if len(self.experiment_paths.learn_log_filepaths_cm) > 0:
            self.file_manager.close_learn_cm_file()
        if len(self.experiment_paths.learn_log_filepaths_g) > 0:
            self.file_manager.close_learn_g_file()
