'''
This file creates files based off of the input hyper parameters. It acts like a hashing function by creating the same file name when the same hyperparameters are selected
but all of the names are unique with each change in a hyperparameter. 
This allows us to keep experiments separate and identifiable. 
This file is also in charge of deleting files that already exist when an experiment is run again. (we might re-run experiments for bug fixes and what not)
It loads the needed filepaths into the file_paths_obj and opens the needed files  and holds/opens/closes the actual file objects
'''

from os.path import join

from play_games.configs.enums import ExperimentType
from play_games.configs.experiment_settings import ExperimentSettings
from play_games.paths import file_paths
from play_games.paths.creator.file_name_directory_elements import FileNameDirectoryElements as name_elements
from ._base import ExperimentPathCreator
from ._learning_experiment import LearningExperimentPathCreator
from ._parameter_experiment import ParameterExperimentPathCreator
from ._tournament import TournamentPathCreator

def get_experiment_specific_path_creator(experiment_settings, experiment_paths)-> ExperimentPathCreator:
    match experiment_settings.experiment_type:
        case ExperimentType.LEARNING_EXPERIMENT:
            return LearningExperimentPathCreator(experiment_settings, experiment_paths)
        case ExperimentType.PARAMETER_EXPERIMENT:
            return ParameterExperimentPathCreator(experiment_settings, experiment_paths)
        case ExperimentType.TOURNAMENT | ExperimentType.RANDOM_TOURNAMENT:
            return TournamentPathCreator(experiment_settings, experiment_paths)


class FilePathCreator:
    
    def __init__(self, experiment_settings: ExperimentSettings, experiment_paths: file_paths.ExperimentPaths):
        self.experiment_settings = experiment_settings
        self.experiment_paths = experiment_paths
        
        self.path_creator = get_experiment_specific_path_creator(experiment_settings, experiment_paths)
        
    def generate_needed_filepaths(self):
        #Each filepath has the same root no matter the type of file that it is. 

        #first task is to set the directory paths for the files
        self.set_directory_paths()

        #second task is to determine the root file name to include in all filepaths
        root_name = self.determine_root_file_name()

        #third task is to create the full filenames and paths
        self.path_creator.create_file_paths(root_name)


    def determine_root_file_name(self):
        if self.experiment_settings.custom_root_name == None:
            #Every file needs to contain the number of games run between each bot pairing and the experiment name. The hyper parameters 
            # will only be included for the type of bots in the tournament
            root_file_name = "{}.{}{}{}{}{}".format(
                self.experiment_settings.config_setting, 
                self.experiment_settings.tournament_setting, 
                name_elements.N_GAMES_PREFIX, 
                self.experiment_settings.n_games, 
                name_elements.B_SIZE_PREFIX,
                self.experiment_settings.board_size,
            )

            root_file_name += self.path_creator.get_experiment_description()

        else:
            root_file_name = self.experiment_settings.custom_root_name

        return root_file_name


    def set_directory_paths(self):
        #We need to generate the parts of the paths that will be used among all paths
        experiment_root_path = self.path_creator.get_root_dir_extension()
        root_path = join(file_paths.results_root, "saved_results", experiment_root_path)

        self.path_creator.create_directories(root_path)

        #now we set the common elements
        self.experiment_paths.round_logs_dir_path = join(root_path, name_elements.RAW_DATA_DIR, name_elements.ROUND_LOGS_DIR)
        self.experiment_paths.parsed_data_dir_path = join(root_path, name_elements.PARSED_DATA_DIR)
        self.experiment_paths.processed_data_dir_path = join(root_path, name_elements.PROCESSED_DATA_DIR)
        self.experiment_paths.cm_stats_dir_path = join(root_path, name_elements.VISUALIZATIONS_DIR, name_elements.FIGURES_DIR, name_elements.CM_STATS_DIR)
        self.experiment_paths.tournament_tables_dir_path = join(root_path, name_elements.VISUALIZATIONS_DIR, name_elements.TABLES_DIR, name_elements.TOURNAMENT_TABLES_DIR)
