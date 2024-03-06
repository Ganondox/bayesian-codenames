from play_games.configs.experiment_settings import ExperimentSettings  

from play_games.paths.file_paths import ExperimentPaths
from play_games.utils.analysis_files.data_processer import DataProcessor
from play_games.utils.analysis_files.data_visualizer import DataVisualizer
from play_games.utils.analysis_files.parsers.data_parser import DataParser
from play_games.configs.enums import ExperimentType

'''
This class is responsible for the stats analysis flow

parse data -> save to file -> process data -> save to file -> visual
'''

class ResultsAnalyzer:
    def __init__(self, experiment_settings: ExperimentSettings, experiment_paths: ExperimentPaths):

        self.experiment_settings = experiment_settings
        self.experiment_paths = experiment_paths
        self.data_parser = DataParser(experiment_paths)
        self.data_processer = DataProcessor(experiment_settings, experiment_paths)
        self.data_visualizer = DataVisualizer(experiment_settings, experiment_paths)


        self.use_preloaded_parsed = False
        self.use_preloaded_processed = False
        self.use_preloaded_visualized = False
        
        self.data_visualizer.figure_creator.fig = not self.use_preloaded_visualized


    def run_analysis(self):
        
        if self.experiment_settings.experiment_type == ExperimentType.LEARNING_EXPERIMENT:

            round_logs = self.experiment_paths.round_log_filepaths
            learn_logs_cm = self.experiment_paths.learn_log_filepaths_cm
            learn_logs_g = self.experiment_paths.learn_log_filepaths_g
            parsed_data_filepaths = self.experiment_paths.parsed_data_filepaths
            processed_data_filepaths = self.experiment_paths.processed_data_filepaths

            if not self.use_preloaded_parsed:
                parsed_data = self.data_parser.parse_data(round_logs, learn_logs_cm, learn_logs_g, parsed_data_filepaths)
            else:
                parsed_data = self.data_parser.load_parsed_data()
            if not self.use_preloaded_processed:
                processed_data = self.data_processer.process_data(parsed_data, processed_data_filepaths)
            else:
                processed_data = self.data_processer.load_processed_data()

            self.data_visualizer.visualize_data(processed_data)

        elif self.experiment_settings.experiment_type == ExperimentType.PARAMETER_EXPERIMENT:

            round_logs = self.experiment_paths.round_log_filepaths

            parsed_data_filepaths = self.experiment_paths.parsed_data_filepaths
            
            processed_data_filepaths = self.experiment_paths.processed_data_filepaths

            if not self.use_preloaded_parsed:
                parsed_data = self.data_parser.parse_data(round_logs, [], [], parsed_data_filepaths)
            else:
                parsed_data = self.data_parser.load_parsed_data()
            if not self.use_preloaded_processed:
                processed_data = self.data_processer.process_data(parsed_data, processed_data_filepaths)
            else:
                processed_data = self.data_processer.load_processed_data()


            if not self.use_preloaded_visualized:
                self.data_visualizer.visualize_data(processed_data)

        else: #this is a tournament
            round_logs = self.experiment_paths.round_log_filepaths
            parsed_data_filepaths = self.experiment_paths.parsed_data_filepaths
            processed_data_filepaths = self.experiment_paths.processed_data_filepaths

            if not self.use_preloaded_parsed:
                parsed_data = self.data_parser.parse_data(round_logs, [], [], parsed_data_filepaths)
            else:
                parsed_data = self.data_parser.load_parsed_data()
            if not self.use_preloaded_processed:
                processed_data = self.data_processer.process_data(parsed_data, processed_data_filepaths)
            else:
                processed_data = self.data_processer.load_processed_data()

            if not self.use_preloaded_visualized:
                self.data_visualizer.visualize_data(processed_data)
                
    def run_analysis_file(self, round_logs, parsed_data_filepaths, processed_data_filepaths):
        if not self.use_preloaded_parsed:
            parsed_data = self.data_parser.parse_data(round_logs, [], [], parsed_data_filepaths)
        else:
            parsed_data = self.data_parser.load_parsed_data()
        if not self.use_preloaded_processed:
            processed_data = self.data_processer.process_data(parsed_data, processed_data_filepaths)
        else:
            processed_data = self.data_processer.load_processed_data()

        if not self.use_preloaded_visualized:
            self.data_visualizer.visualize_data(processed_data)

    


    
