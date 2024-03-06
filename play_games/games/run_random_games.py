import random

from .game import Game
from play_games.utils import utils

class RunRandGames:
    def __init__(self, object_manager):
        self.object_manager = object_manager

        ###LOAD SETTINGS###

        self.CODEMASTERS = self.object_manager.experiment_settings.codemasters

        self.GUESSERS = self.object_manager.experiment_settings.guessers

        self.BOARD_SIZE = self.object_manager.experiment_settings.board_size
        self.CODENAMES_WORDPOOL_FILE = self.object_manager.file_paths_obj.board_words_path

        self.paths = self.object_manager.bot_paths
        self.bot_ai_types = self.object_manager.bot_ai_types


    ###FUNCTIONS###

    def load_words(self):
        # load up words
        f = open(self.CODENAMES_WORDPOOL_FILE, 'r')
        d = f.read()
        l = d.split('\n')
        l = [w.lower() for w in l]
        return l


    def select_game_words(self, codenames_words, seed):
        wlst_cpy = codenames_words.copy()
        sample = []
        random.seed(seed)
        random.shuffle(wlst_cpy)

        for i in range(self.BOARD_SIZE):
            w = wlst_cpy[i]
            sample.append(w)
        return sample

    def get_bot_settings(self, p):
        #We pass in n because it can be changed in a parameter experiment
        bot_settings = self.object_manager.get_new_bot_settings_obj()

        if self.object_manager.experiment_settings.independent_variable != None and self.object_manager.experiment_settings.independent_variable == self.object_manager.experiment_settings.n_associations:
            bot_settings.N_ASSOCIATIONS = self.object_manager.experiment_settings.n_associations[p]
        else:
            bot_settings.N_ASSOCIATIONS = self.object_manager.experiment_settings.n_associations[0]

        if self.object_manager.experiment_settings.independent_variable != None and self.object_manager.experiment_settings.independent_variable == self.object_manager.experiment_settings.ensemble_parameters:
            bot_settings.ENSEMBLE_PARAMS = self.object_manager.experiment_settings.ensemble_parameters[p]
        else:
            bot_settings.ENSEMBLE_PARAMS = self.object_manager.experiment_settings.ensemble_parameters[0]
        
        if self.object_manager.experiment_settings.independent_variable != None and self.object_manager.experiment_settings.independent_variable == self.object_manager.experiment_settings.noise_parameters:
            bot_settings.EMBEDDING_NOISE = self.object_manager.experiment_settings.variable_space[0][p[0]]
            bot_settings.DIST_NOISE = self.object_manager.experiment_settings.variable_space[1][p[1]]
        else:
            bot_settings.EMBEDDING_NOISE = 0
            bot_settings.DIST_NOISE=0

        bot_settings.LOG_FILE = self.object_manager.file_manager.ROUND_FILE
        bot_settings.LEARNING_ALGORITHM = self.object_manager.experiment_settings.learning_algorithm
        bot_settings.INCLUDE_SAME_LM = self.object_manager.experiment_settings.include_same_lm
        bot_settings.MODEL_PATH = self.object_manager.file_paths_obj.model_path
        bot_settings.PRINT_LEARNING = self.object_manager.experiment_settings.print_learning
        if len(self.object_manager.file_paths_obj.learn_log_filepaths_cm) > 0:
            bot_settings.LEARN_LOG_FILE_CM = self.object_manager.file_manager.LEARN_LOG_FILE_CM
        if len(self.object_manager.file_paths_obj.learn_log_filepaths_g) > 0:
            bot_settings.LEARN_LOG_FILE_G = self.object_manager.file_manager.LEARN_LOG_FILE_G

        return bot_settings


    def run_n_games(self, n, bot_type_1, bot_type_2, n1, n2, lp, p, seed=0):
        #Create the settings object to pass into the bots
        bot_settings = self.get_bot_settings(p)

        # init bots
        if n1 is not None:
            bot_settings.BOT_TYPE_SM = bot_type_1
            if n1 < 0:
                bot_settings.DIST_NOISE = -n1
            else:
                bot_settings.EMBEDDING_NOISE = n1
            bot_type_1 = self.object_manager.bot_types.NOISY_DISTANCE_ASSOCIATOR

        codemaster_bot, _ = self.object_manager.bot_initializer.init_bots(bot_type_1, None, bot_settings)
        if n2 is not None:
            bot_settings.BOT_TYPE_G = bot_type_2
            if n2 < 0:
                bot_settings.DIST_NOISE = -n2
            else:
                bot_settings.EMBEDDING_NOISE = n2
            bot_type_2 = self.object_manager.bot_types.NOISY_BASELINE_GUESSER

        _, guesser_bot = self.object_manager.bot_initializer.init_bots(None, bot_type_2, bot_settings)



        # load codenames words
        codenames_words = self.load_words()

        for i in range(n):
            utils.cond_print('Running game {}...'.format(i), self.object_manager.experiment_settings.verbose_flag)
            # select BOARD_SIZE game words
            if self.object_manager.experiment_settings.experiment_type == self.object_manager.experiment_types.LEARNING_EXPERIMENT:
                seed = i + (lp * n)
            else:
                seed = i + seed

            game_words = self.select_game_words(codenames_words, seed)

            # load words into bots
            utils.cond_print('\tloading bots\' dictionaries', self.object_manager.experiment_settings.verbose_flag)
            codemaster_bot.load_dict(game_words)
            guesser_bot.load_dict(game_words)
            utils.cond_print('\tdone', self.object_manager.experiment_settings.verbose_flag)

            # run game
            utils.cond_print('\tbeginning game\n', self.object_manager.experiment_settings.verbose_flag)

            curr_game = Game(bot_type_1, bot_type_2, codemaster_bot, guesser_bot, game_words, seed, self.object_manager.file_manager.ROUND_FILE, self.object_manager.experiment_settings.print_boards)

            curr_game.run()


        utils.cond_print('Successfully ran {} games with {} and {} bots. See game logs for details'.format(n, bot_type_1, bot_type_2), self.object_manager.experiment_settings.verbose_flag)
