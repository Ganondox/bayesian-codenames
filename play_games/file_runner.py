
from paths.creator import FilePathCreator
from utils.object_manager import ObjectManager
from games.run_tournament import RunTournament
from games.run_random_tournament import RunRandTournament

from games.run_learning_experiment import RunLearningExperiment
from games.run_parameter_experiment import RunParameterExperiment
from files.file_cleaner import FileCleaner
from files.file_alignment_checker import FileAlignmentChecker


class FileRunner():
    def __init__(self):
        """The object manager holds all global classes, it avoids many import problems"""
        self.object_manager = ObjectManager()

    def run_tournament(self, seed=0):
        run_tournament = RunTournament(self.object_manager)
        run_tournament.run(seed=seed)
    
    def run_rand_tournament(self, seed=0):
        run_tournament = RunRandTournament(self.object_manager)
        run_tournament.run( seed=seed)

    def run_parameter_experiment(self):
        run_parameter_experiment = RunParameterExperiment(self.object_manager)
        run_parameter_experiment.run()

    def run_learning_experiment(self):
        #There will be some sort of check to see if we just want to analyze results. If so, we do so here
        run_learning_experiment = RunLearningExperiment(self.object_manager)
        run_learning_experiment.run()
    
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
           