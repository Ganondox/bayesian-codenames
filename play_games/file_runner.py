
from paths.creator import FilePathCreator
from play_games.games.run_bayesian_tournament import RunBayesianTournament
from utils.object_manager import ObjectManager
from games.run_tournament import RunTournament

from files.file_cleaner import FileCleaner
from files.file_alignment_checker import FileAlignmentChecker


class FileRunner():
    def __init__(self):
        """The object manager holds all global classes, it avoids many import problems"""
        self.object_manager = ObjectManager()

    def run_tournament(self, seed=0):
        run_tournament = RunTournament(self.object_manager)
        run_tournament.run(seed=seed)

    def run_bayesian_tournament(self, seed=0):
        run_tournament = RunBayesianTournament(self.object_manager)
        run_tournament.run(seed=seed)
    
    def run_analysis(self):
        self.object_manager.results_analyzer.run_analysis()
    
    def clean_logs(self):
        file_cleaner = FileCleaner(self.object_manager)
        file_cleaner.clean_learn_logs()
        file_cleaner.delete_small_files()
        file_cleaner.delete_unmatched_files()

    def generate_file_paths(self):
        path_creator = FilePathCreator(self.object_manager.experiment_settings, self.object_manager.experiment_paths)
        path_creator.generate_needed_filepaths()

    def check_files(self):
        file_alignment_checker = FileAlignmentChecker(self.object_manager)
        return file_alignment_checker.check_alignment()
           