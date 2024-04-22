from play_games.configs.experiment_settings import ExperimentSettings
from play_games.paths import file_paths

class BotSettingsObj:
    N_ASSOCIATIONS = None
    LOG_FILE = None
    LEARN_LOG_FILE_CM = None
    LEARN_LOG_FILE_G = None
    INCLUDE_SAME_LM = None
    BOT_TYPE_SM = None
    BOT_TYPE_G = None
    PRINT_LEARNING = None
    CONSTRUCTOR_PATHS = None
    NOISE_SM = None
    NOISE_G = None
    SAMPLE_SIZE_SM = None
    SAMPLE_SIZE_G = None
    SKIP_THRESHOLD = None
    GUESS_THRESHOLD = None
    AI_TYPE = None


def get_bot_settings(experiment_settings: ExperimentSettings):
    bot_settings = BotSettingsObj()
    bot_settings.N_ASSOCIATIONS = experiment_settings.n_associations
    bot_settings.NOISE_SM = experiment_settings.noise_sm
    bot_settings.NOISE_G = experiment_settings.noise_g
    bot_settings.SAMPLE_SIZE_SM = experiment_settings.sample_size_sm
    bot_settings.SAMPLE_SIZE_G = experiment_settings.sample_size_g
    bot_settings.INCLUDE_SAME_LM = experiment_settings.include_same_lm
    bot_settings.PRINT_LEARNING = experiment_settings.print_learning

    return bot_settings