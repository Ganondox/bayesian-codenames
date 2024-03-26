import os
import sys
if __name__ == "__main__":
    sys.path.insert(0, os.getcwd())

import datetime
import time

from file_runner import FileRunner
from play_games.configs.enums import ExperimentType

#_______________ DEFAULT ARGUMENTS _______________#

seed = 2000
run_experiment = True
config_setting = "BAYES"
iteration_range = None # None defaults to one found in config.ini


#__________________ GLOBALS __________________#

file_runner = FileRunner()
experiment_settings = file_runner.object_manager.experiment_settings


#__________________ MAIN FN __________________#

def main():
    _parse_argv(sys.argv)
    _setup_settings()

    # at this point, we are good to go with our new settings
    if run_experiment: _run_with_settings()

    # file_runner.clean_logs()
    print("all files aligned:", file_runner.check_files())
    file_runner.run_analysis()


#_______________ HELPER FNs _______________#

def _parse_argv(argv):
    global seed, run_experiment, config_setting, iteration_range
    if len(argv) >= 2: # file_runner.py [setting] ... 
        config_setting = argv[1]
        seed = None
    if len(argv) == 3: # file_runner.py [setting] [seed]
        seed = int(argv[2])
        iteration_range[0] += seed
        iteration_range[1] += seed
    elif len(argv) >= 4: # file_runner.py [setting] [start] [finish]
        iteration_range = [int(argv[2]), int(argv[3])]

def _setup_settings():
    if config_setting: experiment_settings.config_setting = config_setting
    experiment_settings.setup()
    if iteration_range: experiment_settings.iteration_range = iteration_range
    if seed: experiment_settings.seed = seed
    
    # Generate new file paths
    file_runner.generate_file_paths()

def _run_with_settings():
    start = time.time()
    match experiment_settings.experiment_type:
        case ExperimentType.LEARNING_EXPERIMENT:  file_runner.run_learning_experiment()
        case ExperimentType.BAYESIAN_TOURNAMENT:  file_runner.run_bayesian_tournament(seed=seed)
        case ExperimentType.TOURNAMENT:           file_runner.run_tournament(seed=seed)
    print(f"Duration {datetime.timedelta(seconds=time.time()-start)}")


if __name__=="__main__":
    main()