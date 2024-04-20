import itertools
import os

import numpy as np
from play_games.bots.types import BotType
from play_games.configs.experiment_settings import ExperimentSettings
from play_games.files.file_manager import FileManager
from play_games.utils import utils
from play_games.paths import file_paths
from .run_bayesian_games import RunBayesianGames
#Pass in settings object to other files and set the needed parameters

def create_path(fp):
    if not os.path.exists(os.path.dirname(fp)):
        os.makedirs(os.path.dirname(fp))

def desc(obj, default):
    if hasattr(obj, "__desc__"):
        return obj.__desc__
    else:
        return default

class RunBayesianTournament:
    def __init__(self, object_manager):
        self.exp_settings: ExperimentSettings = object_manager.experiment_settings
        self.file_manager: FileManager = object_manager.file_manager
        self.experiment_paths: file_paths.ExperimentPaths = object_manager.experiment_paths
        self.run_games = RunBayesianGames(object_manager)
    
    def generate_noise_levels(self,*, embedding, distance):
        emb_stop, num_emb = embedding
        dist_stop, num_dist = distance

        noise_levels = [None, 0]

        emb = np.linspace(emb_stop, 0, num_emb, False)
        dist = -np.linspace(dist_stop, 0, num_dist, False)

        noise_levels.extend(emb)
        noise_levels.extend(dist)

        return noise_levels


    def run(self, seed=0):
        #Get needed information from the experiment_settings.py file
        self.file_manager.open_round_file(0)
        self.file_manager.open_learn_cm_file(0)
        self.file_manager.open_learn_g_file(0)
        
        spymasters = self.exp_settings.spymasters
        guessers = self.exp_settings.guessers
        n = self.exp_settings.n_games 
        
        for b1, b2 in itertools.product(spymasters, guessers):
            noises_cm = np.linspace(0, 2, 6)
            noises_g = np.linspace(0, 2, 6)
            for noise_cm, noise_g in itertools.product(noises_cm, noises_g):
                utils.cond_print(f'Simulating {n} games with {b1} and {b2} with noise {noise_cm} and {noise_g}', self.exp_settings.verbose_flag)
                self.run_games.run_n_games(int(n), b1, b2, noise_cm, noise_g, seed=seed)
        
        self.file_manager.close_learn_cm_file()
        self.file_manager.close_learn_g_file()
        self.file_manager.close_round_file()