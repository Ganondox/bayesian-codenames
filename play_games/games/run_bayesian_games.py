import random

from play_games.bots import bot_settings_obj
from play_games.bots.types import AIType, BotType
from play_games.bots.types.bot_to_ai import get_ai
from play_games.bots.types.bot_to_lm import get_lm
from play_games.utils.object_manager import ObjectManager 

from .game import Game
from play_games.utils import utils
from play_games.paths import file_paths


class RunBayesianGames:
    def __init__(self, object_manager: ObjectManager):
        self.object_manager = object_manager
        self.experiment_paths = object_manager.experiment_paths
        ###LOAD SETTINGS###
        self.BOARD_SIZE = self.object_manager.experiment_settings.board_size


    ###FUNCTIONS###

    def load_words(self):
        # load up words
        return utils.load_word_list(file_paths.board_words_path)


    def select_game_words(self, codenames_words, seed):
        random.seed(seed)
        sample = random.sample(codenames_words, self.BOARD_SIZE)
        return sample

    def get_bot_settings(self):
        #We pass in n because it can be changed in a parameter experiment
        bot_settings = bot_settings_obj.get_bot_settings(self.object_manager.experiment_settings)
        bot_settings.LOG_FILE = self.object_manager.file_manager.ROUND_LOG_FILE
        bot_settings.LEARN_LOG_FILE_CM = self.object_manager.file_manager.LEARN_LOG_FILE_CM

        return bot_settings


    def run_n_games(self, n, bot_type_1, bot_type_2, noise_cm, noise_g, seed=0):
        #Create the settings object to pass into the bots
        bot_settings = self.get_bot_settings()
        bot_settings.LEARN_LOG_FILE_CM.write("STARTING TO LEARN\n")
        
        ### SPYMASTER
        bot_settings.NOISE_SM = noise_cm
        if get_ai(bot_type_1) == AIType.BAYESIAN:
            codemaster_bot, _ = self.object_manager.bot_initializer.init_bots(bot_type_1, None, bot_settings)
        else:
            bot_settings.BOT_TYPE_SM = get_lm(bot_type_1)
            codemaster_bot, _ = self.object_manager.bot_initializer.init_bots(BotType.NOISY_SPYMASTER, None, bot_settings)
        
        ### GUESSER
        bot_settings.NOISE_G = noise_g
        if get_ai(bot_type_2) == AIType.BAYESIAN:
            _, guesser_bot = self.object_manager.bot_initializer.init_bots(None, bot_type_2, bot_settings)
        else:
            bot_settings.BOT_TYPE_G = get_lm(bot_type_2)
            _, guesser_bot = self.object_manager.bot_initializer.init_bots(None, BotType.NOISY_GUESSER, bot_settings)

        # load codenames words
        codenames_words = self.load_words()

        for i in range(n):
            bot_settings.LEARN_LOG_FILE_CM.write(f"GUESSER: {bot_type_2 if not hasattr(guesser_bot, '__desc__') else guesser_bot.__desc__()}\n")
            utils.cond_print('Running game {}...'.format(i), self.object_manager.experiment_settings.verbose_flag)
            # select BOARD_SIZE game words
            game_seed = i + seed

            game_words = self.select_game_words(codenames_words, game_seed)

            # load words into bots
            utils.cond_print('\tloading bots\' dictionaries', self.object_manager.experiment_settings.verbose_flag)
            codemaster_bot.load_dict(game_words)
            guesser_bot.load_dict(game_words)
            utils.cond_print('\tdone', self.object_manager.experiment_settings.verbose_flag)

            # run game
            utils.cond_print('\tbeginning game\n', self.object_manager.experiment_settings.verbose_flag)

            curr_game = Game(bot_type_1, bot_type_2, codemaster_bot, guesser_bot, game_words, game_seed, self.object_manager.file_manager.ROUND_LOG_FILE, self.object_manager.experiment_settings.print_boards)
            curr_game.run()
            bot_settings.LEARN_LOG_FILE_CM.write("ENDING\n")


        utils.cond_print('Successfully ran {} games with {} and {} bots and noises {} and {}. See game logs for details'.format(n, bot_type_1, bot_type_2, noise_cm, noise_g), self.object_manager.experiment_settings.verbose_flag)