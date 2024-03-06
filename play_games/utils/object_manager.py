
import __init__
from play_games.paths.file_paths import ExperimentPaths

#object imports
from play_games.configs.experiment_settings import ExperimentSettings
from files.file_manager import FileManager
from utils.results_analyzer import ResultsAnalyzer
from play_games.bots.builders.bot_initializer import BotInitializer


class ObjectManager:

    def __init__(self):
        self.bot_initializer: BotInitializer = BotInitializer()
        self.experiment_paths = ExperimentPaths()
        self.experiment_settings: ExperimentSettings = ExperimentSettings()
        self.file_manager: FileManager = FileManager(self.experiment_settings, self.experiment_paths)
        self.results_analyzer: ResultsAnalyzer = ResultsAnalyzer(self.experiment_settings, self.experiment_paths)

    