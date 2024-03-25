from play_games.bots.ai_components.bayesian_components import LANGUAGE_MODELS, InternalGuesser
from play_games.bots.bot_settings_obj import BotSettingsObj
from play_games.bots.spymasters.bayesian_spymaster import BayesianSpymaster
from play_games.bots.types import AIType, BotType
from play_games.games.enums import Color
from play_games.paths import bot_paths
from play_games.bots.types.bot_to_ai import get_ai
from play_games.bots.types.bot_to_lm import get_lm
from play_games.bots.builders.constructor import BotConstructorType

class BotInitializer():
    def __init__(self):
        pass

    '''
    We use the ai_type to determine the constructor we need because each constructor is built for a specific ai_type and the filepaths determine which lm is used. 
    If we simply used the bot_type to determine which constructor to call, we would have a lot more conditional blocks and/or conditions. 
    '''
    def init_bots(self, bot_type_1: BotType, bot_type_2: BotType, bot_settings: BotSettingsObj):
        spymaster_bot = None
        guesser_bot = None

        if bot_type_1 != None:

            bot_ai_type = get_ai(bot_type_1)
            bot_settings.CONSTRUCTOR_PATHS = bot_paths.get_paths_for_bot(bot_type_1)

            match bot_ai_type:
                case AIType.DISTANCE_ASSOCIATOR:
                    spymaster_bot = BotConstructorType.DISTANCE_ASSOCIATOR_AI_SPYMASTER.build()
                case AIType.BAYESIAN:
                    spymaster_bot = self.initialize_bayesian_spymaster(bot_settings)
                case _:
                    print("Error loading spymaster")
                    return

            spymaster_bot.initialize(bot_settings)

        if bot_type_2 != None:

            bot_ai_type = get_ai(bot_type_2)
            bot_settings.CONSTRUCTOR_PATHS = bot_paths.get_paths_for_bot(bot_type_2)

            match bot_ai_type:
                case AIType.BASELINE:
                    guesser_bot = BotConstructorType.VECTOR_BASELINE_GUESSER.build()
                case AIType.NOISY:
                    bot_settings.CONSTRUCTOR_PATHS = bot_paths.get_vector_path_for_lm(bot_settings.BOT_TYPE_G)
                    guesser_bot = BotConstructorType.NOISY_GUESSER.build()
                case _:
                    print("Error loading guesser")
                    return 
            guesser_bot.initialize(bot_settings)

        return spymaster_bot, guesser_bot


    def initialize_bayesian_spymaster(self, bot_settings_obj):
        guessers = [ InternalGuesser(lm) for lm in LANGUAGE_MODELS ]
        team = Color.TEAM
        prior = {g:1/len(guessers) for g in guessers}
        noise = 1.7 #1.7 # try other values
        samples = 10 # try other values
        name = "Bayesian"
        return BayesianSpymaster(team, guessers, prior, noise, samples, name)        
