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
    ITERATION_RANGE = "iteration_range"
    INCLUDE_SAME_LM = "include_same_lm"
    SPYMASTER_NOISE = "spymaster_noise"
    GUESSER_NOISE = "guesser_noise"
    DETECT = "detect"
    INDEPENDENT_VARIABLE = "independent_variable"
    VARIABLE_SPACE = "variable_space"
    VERBOSE_FLAG = "verbose_flag"
    PRINT_BOARDS = "print_boards"
    PRINT_LEARNING = "print_learning"
    SPYMASTER_SAMPLE_SIZE = "spymaster_sample_size"
    GUESSER_SAMPLE_SIZE = "guesser_sample_size"

class ExperimentType(StrEnum):
    LEARNING_EXPERIMENT = "learning experiment"
    PARAMETER_EXPERIMENT = "parameter experiment"
    BAYESIAN_TOURNAMENT = "bayesian tournament"
    TOURNAMENT = "tournament"

class Parameters(StrEnum):
    N_ASSOCIATIONS = "Number of Associations"
