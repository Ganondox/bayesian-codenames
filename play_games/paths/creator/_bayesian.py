from ._base import ExperimentPathCreator
from play_games.paths.creator.file_name_directory_elements import FileNameDirectoryElements as name_elements
from os.path import join

from .__tools import create_round_logs_files

class BayesianPathCreator(ExperimentPathCreator):
    
    def get_experiment_description(self):
        return ""

    def get_root_dir_extension(self):
        if self.experiment_settings.custom_root_name:
            return self.experiment_settings.custom_root_name
        return "bayesian_tournament"

    def create_directories(self, root_dir):
        self.experiment_paths.learn_logs_dir_path = join(root_dir, name_elements.RAW_DATA_DIR, name_elements.LEARN_LOGS_DIR)

    def create_file_paths(self, filename_prefix):
        create_round_logs_files(self.experiment_paths, filename_prefix, self.experiment_settings.seed)
        self._create_learn_log_paths(filename_prefix, self.experiment_settings.seed, self.experiment_paths.learn_log_filepaths_cm, self.experiment_paths.learn_log_filepaths_g)

    def _create_learn_log_paths(self, filename_prefix, iteration, paths_cm, paths_g):
        dir = self.experiment_paths.learn_logs_dir_path
        this_name = f"{name_elements.LEARN_LOG_PREFIX}_{filename_prefix}_{iteration}_CM{name_elements.LEARN_LOG_FILE_TYPE}"
        paths_cm.append(join(dir, this_name))
        this_name = f"{name_elements.LEARN_LOG_PREFIX}_{filename_prefix}_{iteration}_G{name_elements.LEARN_LOG_FILE_TYPE}"
        paths_g.append(join(dir, this_name))
