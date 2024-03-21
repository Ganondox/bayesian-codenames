'''
This file will play 30 games between 2 bots that are passed in 

When you add a bot, make sure you add it's lm path to paths and add the bot type to BotTypes.py and put it into the spymaster or guesser list

authors: Kyle Rogers and Spencer Brosnahan
'''
import random
import numpy as np

from .game import Game
from play_games.utils import utils
from play_games.bots import bot_settings_obj
from play_games.configs.enums import ExperimentType, IndependentVariables
from play_games.utils.object_manager import ObjectManager
from play_games.paths import file_paths

class RunGames:
    def __init__(self, object_manager: ObjectManager):
        self.object_manager = object_manager
        self.experiment_paths = object_manager.experiment_paths

        ###LOAD SETTINGS###

        self.SPYMASTERS = self.object_manager.experiment_settings.spymasters

        self.GUESSERS = self.object_manager.experiment_settings.guessers

        self.BOARD_SIZE = self.object_manager.experiment_settings.board_size


    ###FUNCTIONS###

    def load_words(self):
        # load up words
        return utils.load_word_list(file_paths.board_words_path)


    def select_game_words(self, codenames_words, seed):
        random.seed(seed)
        sample = random.sample(codenames_words, self.BOARD_SIZE)
        return sample

    def get_bot_settings(self, p):
        #We pass in n because it can be changed in a parameter experiment
        bot_settings = bot_settings_obj.get_bot_settings(self.object_manager.experiment_settings)

        if self.object_manager.experiment_settings.experiment_type == ExperimentType.PARAMETER_EXPERIMENT:
            match self.object_manager.experiment_settings.independent_variable:
                case IndependentVariables.N_ASSOCIATIONS:
                    bot_settings.N_ASSOCIATIONS = self.object_manager.experiment_settings.variable_space[p]
                

        bot_settings.LOG_FILE = self.object_manager.file_manager.ROUND_LOG_FILE
        if len(self.experiment_paths.learn_log_filepaths_cm) > 0:
            bot_settings.LEARN_LOG_FILE_CM = self.object_manager.file_manager.LEARN_LOG_FILE_CM
        if len(self.experiment_paths.learn_log_filepaths_g) > 0:
            bot_settings.LEARN_LOG_FILE_G = self.object_manager.file_manager.LEARN_LOG_FILE_G

        return bot_settings


    def run_n_games(self, n, bot_type_1, bot_type_2, lp, p, seed=0):
        #Create the settings object to pass into the bots
        bot_settings = self.get_bot_settings(p)

        # init bots
        spymaster_bot, guesser_bot = self.object_manager.bot_initializer.init_bots(bot_type_1, bot_type_2, bot_settings)

        # load codenames words
        codenames_words = self.load_words()

        for i in range(n):
            utils.cond_print('Running game {}...'.format(i), self.object_manager.experiment_settings.verbose_flag)
            # select BOARD_SIZE game words
            if self.object_manager.experiment_settings.experiment_type == ExperimentType.LEARNING_EXPERIMENT:
                seed = i + (lp * n)
            else:
                seed = i + seed

            game_words = self.select_game_words(codenames_words, seed)

            # load words into bots
            utils.cond_print('\tloading bots\' dictionaries', self.object_manager.experiment_settings.verbose_flag)
            spymaster_bot.load_dict(game_words)
            guesser_bot.load_dict(game_words)
            utils.cond_print('\tdone', self.object_manager.experiment_settings.verbose_flag)

            # run game
            utils.cond_print('\tbeginning game\n', self.object_manager.experiment_settings.verbose_flag)

            curr_game = Game(bot_type_1, bot_type_2, spymaster_bot, guesser_bot, game_words, seed, self.object_manager.file_manager.ROUND_LOG_FILE, self.object_manager.experiment_settings.print_boards)
            curr_game.run()


        utils.cond_print('Successfully ran {} games with {} and {} bots. See game logs for details'.format(n, bot_type_1, bot_type_2), self.object_manager.experiment_settings.verbose_flag)