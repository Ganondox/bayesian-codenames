from ._base import ExperimentPathCreator
from play_games.paths.creator.file_name_directory_elements import FileNameDirectoryElements as name_elements

from .__tools import create_round_logs_files

class TournamentPathCreator(ExperimentPathCreator):
    
    def get_experiment_description(self):
        return ""

    def get_root_dir_extension(self):
        return name_elements.TOURNAMENTS_DIR

    def create_directories(self, root_dir):
        pass

    def create_file_paths(self, filename_prefix):
        create_round_logs_files(self.experiment_paths, filename_prefix, self.experiment_settings.seed)
