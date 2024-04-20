from copy import copy
from play_games.bots.ai_components.bayesian_components import LANGUAGE_MODELS, InternalGuesser
from play_games.bots.bot_settings_obj import BotSettingsObj
from play_games.bots.guessers.bayesian_guesser import BayesianGuesser
from play_games.bots.spymasters.bayesian_spymaster import BayesianSpymaster
from play_games.bots.spymasters.noisy_spymaster import NoisySpymaster
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

        bot_settings_spymaster: BotSettingsObj = copy(bot_settings)
        bot_settings_guesser: BotSettingsObj = copy(bot_settings)

        if bot_type_1 != None:

            bot_ai_type = get_ai(bot_type_1)
            bot_settings_spymaster.CONSTRUCTOR_PATHS = bot_paths.get_paths_for_bot(bot_type_1)

            match bot_ai_type:
                case AIType.DISTANCE_ASSOCIATOR:
                    spymaster_bot = BotConstructorType.DISTANCE_ASSOCIATOR_AI_SPYMASTER.build()
                case AIType.NOISY:
                    spymaster_bot = NoisySpymaster(bot_settings_spymaster.BOT_TYPE_SM)
                case AIType.BAYESIAN:
                    spymaster_bot = self.initialize_bayesian_spymaster(bot_settings_spymaster)
                case _:
                    print("Error loading spymaster")
                    return

            spymaster_bot.initialize(bot_settings_spymaster)

        if bot_type_2 != None:

            bot_ai_type = get_ai(bot_type_2)
            bot_settings_guesser.CONSTRUCTOR_PATHS = bot_paths.get_paths_for_bot(bot_type_2)

            match bot_ai_type:
                case AIType.BASELINE:
                    guesser_bot = BotConstructorType.VECTOR_BASELINE_GUESSER.build()
                case AIType.NOISY:
                    bot_settings_guesser.CONSTRUCTOR_PATHS = bot_paths.get_vector_path_for_lm(bot_settings_guesser.BOT_TYPE_G)
                    guesser_bot = BotConstructorType.NOISY_GUESSER.build()
                case AIType.BAYESIAN:
                    guesser_bot = self.initialize_bayesian_guesser(bot_settings_guesser)
                case _:
                    print("Error loading guesser")
                    return 
            guesser_bot.initialize(bot_settings_guesser)

        return spymaster_bot, guesser_bot


    def initialize_bayesian_spymaster(self, bot_settings_obj: BotSettingsObj):
        guessers = [ InternalGuesser(lm, bot_settings_obj.N_ASSOCIATIONS) for lm in LANGUAGE_MODELS ]
        team = Color.TEAM
        prior = {g:1/len(guessers) for g in guessers}
        noise = bot_settings_obj.NOISE_SM #1.7 # try other values
        samples = bot_settings_obj.SAMPLE_SIZE_SM # try other values
        name = "Bayesian Spymaster"
        return BayesianSpymaster(team, guessers, prior, noise, samples, name)        
    
    def initialize_bayesian_guesser(self, bot_settings_obj: BotSettingsObj):
        team = Color.TEAM
        noise = bot_settings_obj.NOISE_G #1.7 # try other values
        samples = bot_settings_obj.SAMPLE_SIZE_G # try other values
        name = "Bayesian Guesser"

        spymasters = []
        for lm in LANGUAGE_MODELS:
            bot_settings_obj.BOT_TYPE_SM = lm
            bot_settings_obj.NOISE_SM = 0
            spymasters.append(self.init_bots(BotType.NOISY_SPYMASTER, None, bot_settings=bot_settings_obj)[0])

        prior = {g:1/len(spymasters) for g in spymasters}

        return BayesianGuesser(team, spymasters, prior, noise, samples, name)  
