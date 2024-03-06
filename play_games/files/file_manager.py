'''
This file creates files based off of the input hyper parameters. It acts like a hashing function by creating the same file name when the same hyperparameters are selected
but all of the names are unique with each change in a hyperparameter. 
This allows us to keep experiments separate and identifiable. 
This file is also in charge of deleting files that already exist when an experiment is run again. (we might re-run experiments for bug fixes and what not)
It loads the needed filepaths into the file_paths_obj and opens the needed files  and holds/opens/closes the actual file objects
'''

from typing import TextIO

from play_games.utils import utils
from play_games.configs.experiment_settings import ExperimentSettings
from play_games.paths import file_paths

class FileManager:
    
    def __init__(self, experiment_settings: ExperimentSettings, experiment_paths: file_paths.ExperimentPaths):
        self.experiment_settings = experiment_settings
        self.experiment_paths = experiment_paths
        

    #These are the actual file variables that are opened and closed throughout the program
    ROUND_LOG_FILE: TextIO = None
    LEARN_LOG_FILE_CM : TextIO= None
    LEARN_LOG_FILE_G: TextIO = None

    def open_round_file(self, index):
        self.close_round_file()
        self.ROUND_LOG_FILE = self.__open(self.experiment_paths.round_log_filepaths[index])

    def close_round_file(self):
        self.__close(self.ROUND_LOG_FILE)

    def open_learn_cm_file(self, index):
        self.close_learn_cm_file()
        self.LEARN_LOG_FILE_CM = self.__open(self.experiment_paths.learn_log_filepaths_cm[index])

    def close_learn_cm_file(self):
        self.__close(self.LEARN_LOG_FILE_CM)

    def open_learn_g_file(self, index):
        self.close_learn_g_file()
        self.LEARN_LOG_FILE_G = self.__open(self.experiment_paths.learn_log_filepaths_g[index])

    def close_learn_g_file(self):
        self.__close(self.LEARN_LOG_FILE_G)

    def __open(self, file: TextIO):
        utils.create_path(file)
        return open(file, 'w+', encoding='utf8')

    def __close(self, file: TextIO):
        if file and not file.closed:
            file.close()