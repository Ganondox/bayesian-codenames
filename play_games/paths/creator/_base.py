
import abc

from play_games.configs.experiment_settings import ExperimentSettings
from play_games.paths.file_paths import ExperimentPaths


class ExperimentPathCreator(abc.ABC):

    def __init__(self, experiment_settings, experiment_paths):
        self.experiment_settings: ExperimentSettings = experiment_settings
        self.experiment_paths: ExperimentPaths = experiment_paths

    @abc.abstractmethod
    def get_experiment_description(self):
        pass

    @abc.abstractmethod
    def get_root_dir_extension(self):
        pass

    @abc.abstractmethod
    def create_directories(self, root_dir):
        pass

    @abc.abstractmethod
    def create_file_paths(self, filename_prefix):
        pass