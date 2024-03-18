from os.path import join
from play_games.utils.analysis_files.analysis_utils import MAIN_STATS_KEYS

from play_games.paths.creator.file_name_directory_elements import FileNameDirectoryElements as name_elements
from ._base import ExperimentPathCreator
from .__tools import create_round_logs_files

class ParameterExperimentPathCreator(ExperimentPathCreator):

    def get_experiment_description(self):
        return name_elements.IND_VAR_VAL

    def get_root_dir_extension(self):
        return name_elements.PARAMETER_EXPERIMENTS_DIR

    def create_directories(self, root_dir):
        self.experiment_paths.param_comparison_figs_dir_path = join(root_dir, name_elements.VISUALIZATIONS_DIR, name_elements.FIGURES_DIR, name_elements.PARAM_COMPARISON_FIGS_DIR)
        #This is set as directory paths because we can just append to the filepath
        #there are is at most one per experiment. 
        self.experiment_paths.param_experiment_analysis_filepath = join(root_dir, name_elements.PARAM_EXPERIMENT_ANALYSES_DIR)

    def create_file_paths(self, filename_prefix):
        #The parameter that is being changed will be specified in the experiment name
        parameters = self.experiment_settings.variable_space

        lower = parameters[0]
        upper = parameters[-1]
        param_range = f"{lower}-{upper}"

        #For every pair (and average of all pairs) and every stat, we want a different figure
        for stat in MAIN_STATS_KEYS:
            for cm in self.experiment_settings.spymasters:
                for g in self.experiment_settings.guessers:

                    if cm not in self.experiment_paths.param_comparison_fig_filepaths:
                        self.experiment_paths.param_comparison_fig_filepaths[cm] = {}
                    if g not in self.experiment_paths.param_comparison_fig_filepaths[cm]:
                        self.experiment_paths.param_comparison_fig_filepaths[cm][g] = {}


                    fname = f"{name_elements.PARAMETER_COMPARISON_FIGURE_PREFIX}{stat}_{cm}-{g}_{filename_prefix}{param_range}{name_elements.PARAMETER_COMPARISON_FIGURE_FILE_TYPE}"
                    dir = self.experiment_paths.param_comparison_figs_dir_path
                    self.experiment_paths.param_comparison_fig_filepaths[cm][g][stat] = join(dir, stat, fname)
                    
            #add the average for all as well
            fname = name_elements.PARAMETER_COMPARISON_FIGURE_PREFIX + stat + "_avg_perf_" + \
                    filename_prefix + param_range + name_elements.PARAMETER_COMPARISON_FIGURE_FILE_TYPE
            dir = self.experiment_paths.param_comparison_figs_dir_path

            if "avg" not in self.experiment_paths.param_comparison_fig_filepaths:
                self.experiment_paths.param_comparison_fig_filepaths['avg'] = {}
            self.experiment_paths.param_comparison_fig_filepaths["avg"][stat] = join(dir, stat, fname)
        
        for p in parameters:
            create_round_logs_files(self.experiment_paths, filename_prefix, p)