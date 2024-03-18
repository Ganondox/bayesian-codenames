import os
from play_games.utils import utils
from .run_random_games import RunRandGames
#Pass in settings object to other files and set the needed parameters

def create_path(fp):
    if not os.path.exists(os.path.dirname(fp)):
        os.makedirs(os.path.dirname(fp))

def desc(obj, default):
    if hasattr(obj, "__desc__"):
        return obj.__desc__
    else:
        return default

class RunRandTournament:
    def __init__(self, object_manager):
        self.object_manager = object_manager
        self.run_games = RunRandGames(object_manager)
        self.lower = None 
        self.upper = None 

    def run(self, lp=0, p=0, parrallel=False, seed=0):
        #Get needed information from the experiment_settings.py file
        spymasters = self.object_manager.experiment_settings.spymasters
        guessers = self.object_manager.experiment_settings.guessers
        n = self.object_manager.experiment_settings.n_games 
        is_learning_experiment = False

        if self.lower == None: 
            self.lower = 0
            self.upper = 0
            
        if self.object_manager.experiment_settings.experiment_type == self.object_manager.experiment_types.PARAMETER_EXPERIMENT:
            fi = p
        else:
            fi = (lp - self.lower)
        if self.object_manager.experiment_settings.experiment_type == self.object_manager.experiment_types.PARAMETER_EXPERIMENT:
            path = self.object_manager.file_paths_obj.round_log_filepaths[fi]
        else:
            path = self.object_manager.file_paths_obj.round_log_filepaths[fi]
        
        create_path(path)
        self.object_manager.file_manager.ROUND_FILE = open(path, 'w+', encoding='utf8')

        if len(self.object_manager.file_paths_obj.learn_log_filepaths_cm) > 0:
            create_path(self.object_manager.file_paths_obj.learn_log_filepaths_cm[fi])
            self.object_manager.file_manager.LEARN_LOG_FILE_CM = open(self.object_manager.file_paths_obj.learn_log_filepaths_cm[fi], 'w+', encoding='utf8')
            is_learning_experiment = True
        if len(self.object_manager.file_paths_obj.learn_log_filepaths_g) > 0:
            create_path(self.object_manager.file_paths_obj.learn_log_filepaths_g[fi])
            self.object_manager.file_manager.LEARN_LOG_FILE_G = open(self.object_manager.file_paths_obj.learn_log_filepaths_g[fi], 'w+', encoding='utf8')
            is_learning_experiment = True

        i = 0
        
        for b1 in spymasters:
            i += 1
            for noise_cm in [None, 0, 1, -0.02]:
                for b2 in guessers:
                    for noise_g in [None, 1, -0.02]:
                        #I need to check that at least one of the bots is ensemble if this is a learning experiment
                        if noise_cm and noise_cm != 0 and noise_g and noise_g != 0:
                            continue
                        utils.cond_print(f'Simulating {n} games with {b1} and {b2}', self.object_manager.experiment_settings.verbose_flag)
                        self.run_games.run_n_games(int(n), b1, b2, noise_cm, noise_g, lp, p, seed=seed)

        self.object_manager.file_manager.ROUND_FILE.close()

        if len(self.object_manager.file_paths_obj.learn_log_filepaths_cm) > 0:
            self.object_manager.file_manager.LEARN_LOG_FILE_CM.close()
        if len(self.object_manager.file_paths_obj.learn_log_filepaths_g) > 0:
            self.object_manager.file_manager.LEARN_LOG_FILE_G.close()
