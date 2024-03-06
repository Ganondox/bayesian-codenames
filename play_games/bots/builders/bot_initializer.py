from play_games.bots.ai_components.ensemble_ai_components.ensemble_utils import EnsembleCodemasterBots, EnsembleGuesserBots, LearningAlgorithms
from play_games.bots.codemasters.noisy_distance_associator_codemaster import NoisyDistanceAssociatorAICodemaster
from play_games.bots.guessers.noisy_ai_guesser import NoisyAIGuesser
from play_games.bots.bot_settings_obj import BotSettingsObj
from play_games.bots.types import AIType, BotType
from play_games.paths import bot_paths
from play_games.bots.types.bot_to_ai import get_ai
from play_games.bots.types.bot_to_lm import get_lm
from play_games.bots.builders.constructor import BotConstructorType

class BotInitializer():
    def __init__(self):
        self.ensemble_cm_types = EnsembleCodemasterBots()
        self.ensemble_g_types = EnsembleGuesserBots()
        self.orig_alg = None

    '''
    We use the ai_type to determine the constructor we need because each constructor is built for a specific ai_type and the filepaths determine which lm is used. 
    If we simply used the bot_type to determine which constructor to call, we would have a lot more conditional blocks and/or conditions. 
    '''
    def init_bots(self, bot_type_1: BotType, bot_type_2: BotType, bot_settings: BotSettingsObj):
        codemaster_bot = None
        guesser_bot = None
        if self.orig_alg == None: self.orig_alg = bot_settings.LEARNING_ALGORITHM #assign this if it is the first time it is called

        if bot_type_1 != None:

            bot_ai_type = get_ai(bot_type_1)
            bot_settings.CONSTRUCTOR_PATHS = bot_paths.get_paths_for_bot(bot_type_1)

            match bot_ai_type:
                case AIType.DISTANCE_ASSOCIATOR:
                    codemaster_bot = BotConstructorType.DISTANCE_ASSOCIATOR_AI_CODEMASTER.build()
                case AIType.DISTANCE_ENSEMBLE:
                    codemaster_bot = self.initialize_ensemble_cm(AIType.DISTANCE_ENSEMBLE, bot_type_2, bot_settings)
                case AIType.RANDOM_DISTANCE_ENSEMBLE:
                    codemaster_bot = self.initialize_ensemble_cm(AIType.RANDOM_DISTANCE_ENSEMBLE, bot_type_2, bot_settings)
                case AIType.NOISY_DISTANCE_ASSOCIATOR:
                    codemaster_bot = self.initialize_noisy_cm(bot_settings)
                case _:
                    print("Error loading codemaster")
                    return

            codemaster_bot.initialize(bot_settings)

        if bot_type_2 != None:

            bot_ai_type = get_ai(bot_type_2)
            bot_settings.CONSTRUCTOR_PATHS = bot_paths.get_paths_for_bot(bot_type_2)

            match bot_ai_type:
                case AIType.BASELINE:
                    guesser_bot = BotConstructorType.VECTOR_BASELINE_GUESSER.build()
                case AIType.DISTANCE_ENSEMBLE:
                    guesser_bot = self.initialize_ensemble_g(AIType.DISTANCE_ENSEMBLE, bot_type_1, bot_settings)
                case AIType.RANDOM_DISTANCE_ENSEMBLE:
                    guesser_bot = self.initialize_ensemble_g(AIType.RANDOM_DISTANCE_ENSEMBLE, bot_type_1, bot_settings)
                case AIType.NOISY_BASELINE:
                    guesser_bot = self.initialize_noisy_g(bot_settings)
                case _:
                    print("Error loading guesser")
                    return 
            guesser_bot.initialize(bot_settings)

        return codemaster_bot, guesser_bot

    '''
    Ensemble bots are special because they depend on other bots. To avoid a lot of code duplication and unnecessary dependencies within
    the bot itself, we will manage the selection of bots to be used and their initialization here.  
    '''
    def initialize_ensemble_cm(self, ai_type, guesser_type, bot_settings):    
        config_bot_types = self.ensemble_cm_types.get_ensemble_cm_bots(ai_type)
        assert(bot_settings.INCLUDE_SAME_LM != None)
        if(bot_settings.INCLUDE_SAME_LM): 
            bot_types = config_bot_types[:]
        else: 
            bot_types = [bot for bot in config_bot_types if get_lm(bot) != get_lm(guesser_type)]
        
        # Initialize bots
        bots = [self.init_bots(bot, None, bot_settings)[0] for bot in bot_types]

        match ai_type:
            case AIType.DISTANCE_ENSEMBLE:
                bot_settings.AI_TYPE = AIType.DISTANCE_ENSEMBLE
                bot_settings.LEARNING_ALGORITHM = self.orig_alg
                instance = BotConstructorType.ENSEMBLE_AI_CODEMASTER.build()
            case AIType.RANDOM_DISTANCE_ENSEMBLE:
                bot_settings.AI_TYPE = AIType.RANDOM_DISTANCE_ENSEMBLE
                bot_settings.LEARNING_ALGORITHM = "T4"
                bot_settings.LEARN_LOG_FILE_CM = None 
                instance = BotConstructorType.ENSEMBLE_AI_CODEMASTER.build()
            case _:
                print("Error loading ensemble codemaster")
                return

        args = (bots, bot_types, guesser_type, bot_settings)
        instance.initialize(args)
        return instance
    
    def initialize_ensemble_g(self, ai_type, codemaster_type, bot_settings):
        config_bot_types = self.ensemble_g_types.get_ensemble_g_bots(ai_type)
        assert(bot_settings.INCLUDE_SAME_LM != None)

        if(bot_settings.INCLUDE_SAME_LM): 
            bot_types = config_bot_types[:]
        else: 
            bot_types = [bot for bot in config_bot_types if get_lm(bot) != get_lm(codemaster_type)]
        
        # Initialize bots
        bots = [self.init_bots(None, bot, bot_settings)[1] for bot in bot_types]

        match ai_type:
            case AIType.DISTANCE_ENSEMBLE:
                bot_settings.AI_TYPE = AIType.DISTANCE_ENSEMBLE
                bot_settings.LEARNING_ALGORITHM = self.orig_alg
            case AIType.RANDOM_DISTANCE_ENSEMBLE:
                bot_settings.AI_TYPE = AIType.RANDOM_DISTANCE_ENSEMBLE
                bot_settings.LEARNING_ALGORITHM = LearningAlgorithms.T4
                bot_settings.LEARN_LOG_FILE_G = None 
            case _:
                print("Error loading ensemble codemaster")
                return
            
        instance = BotConstructorType.ENSEMBLE_AI_GUESSER.build()
        args = (bots, bot_types, codemaster_type, bot_settings)
        instance.initialize(args)
        return instance

    
    def initialize_noisy_cm(self, bot_settings):
        bot_type = bot_settings.BOT_TYPE_SM
        bot_settings.CONSTRUCTOR_PATHS = bot_paths.get_paths_for_bot(bot_type)

        return NoisyDistanceAssociatorAICodemaster()

    def initialize_noisy_g(self, bot_settings):
        bot_type = bot_settings.BOT_TYPE_G
        bot_settings.CONSTRUCTOR_PATHS = bot_paths.get_paths_for_bot(bot_type)

        return NoisyAIGuesser()