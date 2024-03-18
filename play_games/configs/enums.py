from enum import StrEnum


class ConfigKeys(StrEnum):
    N_GAMES = "n_games"
    N_ASSOCIATIONS = "n_associations"
    BOARD_SIZE = "board_size"
    TOURNAMENT_SETTING = "tournament_setting"
    SPYMASTERS = "spymasters"
    GUESSERS = "guessers"
    EXPERIMENT_TYPE = "experiment_type"
    CUSTOM_ROOT_NAME = "custom_root_name"
    LEARNING_ALGORITHM = "learning_algorithm"
    IS_PARAMETER_OPTIMIZATION = "is_parameter_optimization"
    CURR_ITERATION = "curr_iteration"
    ITERATION_RANGE = "iteration_range"
    INCLUDE_SAME_LM = "include_same_lm"
    CONVERGENCE_THRESHOLD = "convergence_threshold"
    ENSEMBLE_PARAMETERS = "ensemble_parameters"
    NOISE_PARAMETERS = "noise_parameters"
    DETECT = "detect"
    INDEPENDENT_VARIABLE = "independent_variable"
    VARIABLE_SPACE = "variable_space"
    VERBOSE_FLAG = "verbose_flag"
    PRINT_BOARDS = "print_boards"
    PRINT_LEARNING = "print_learning"

class ExperimentType(StrEnum):
    LEARNING_EXPERIMENT = "learning experiment"
    PARAMETER_EXPERIMENT = "parameter experiment"
    RANDOM_TOURNAMENT = "random tournament"
    TOURNAMENT = "tournament"

class Parameters(StrEnum):
    N_ASSOCIATIONS = "Number of Associations"

class IndependentVariables(StrEnum):
    N_ASSOCIATIONS = ConfigKeys.N_ASSOCIATIONS
    ENSEMBLE_PARAMETERS = ConfigKeys.ENSEMBLE_PARAMETERS
    NOISE_PARAMETERS = ConfigKeys.NOISE_PARAMETERS