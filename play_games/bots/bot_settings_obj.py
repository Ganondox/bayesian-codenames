from play_games.configs.experiment_settings import ExperimentSettings
from play_games.paths import file_paths

class BotSettingsObj:
    N_ASSOCIATIONS = None
    LOG_FILE = None
    LEARN_LOG_FILE_CM = None
    LEARN_LOG_FILE_G = None
    INCLUDE_SAME_LM = None
    MODEL_PATH = None
    BOT_TYPE_SM = None
    BOT_TYPE_G = None
    PRINT_LEARNING = None
    CONSTRUCTOR_PATHS = None
    EMBEDDING_NOISE = None
    AI_TYPE = None

def get_bot_settings(experiment_settings: ExperimentSettings):
    bot_settings = BotSettingsObj()
    bot_settings.N_ASSOCIATIONS = experiment_settings.n_associations
    bot_settings.EMBEDDING_NOISE = experiment_settings.noise_parameters
    bot_settings.INCLUDE_SAME_LM = experiment_settings.include_same_lm
    bot_settings.MODEL_PATH = file_paths.model_path
    bot_settings.PRINT_LEARNING = experiment_settings.print_learning

    return bot_settings