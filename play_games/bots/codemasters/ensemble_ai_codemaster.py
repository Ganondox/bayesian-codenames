from copy import deepcopy

import random

#Bot libraries
from bots.ai_components.ensemble_ai_components.ensemble_ai import EnsambleAI
from bots.ai_components.ensemble_ai_components.ensemble_utils import LearningAlgorithms
from play_games.bots.ai_components.ensemble_ai_components.strategies import StrategyFour, StrategyThree
from play_games.bots.codemasters.codemaster import Codemaster
from play_games.games.enums import GameCondition


class EnsembleAICodemaster(EnsambleAI, Codemaster):

    def __init__(self):
        random.seed(42)
        self.player_words = None
        self.opponent_words = None
        self.bystander_words = None
        self.assassin_word = None

        #We will use bot_clues_generated in order to determine the bots involved and then we'll put them in bots_used
        self.bot_clues_generated = {}
        self.bots_used = {}
        self.bot_to_use = None
        self.total_rounds = 0

        #These help us decide which bots to select. Usage dict helps us to see which ones we haven't tried. 
        #bot weights is what we use to select the bot (Max or min value is chosen)
        self.usage_dict = {}
        self.bot_weights = {}


    def initialize(self, args):
        '''
        We pass in args to mimic having different constructors. If the argument passed in is of the indicated type, we don't want to do anything. 
        '''
        c_name = args.__class__.__name__ 
        if c_name == "BotSettingsObj":
            return

        assert(len(args) == 4)
        bots = args[0]
        bot_types = args[1]
        tm_type = args[2]
        bot_settings = args[3]
        super().__init__(bots, bot_types, bot_settings)

        #Create an instance of the strategy we are using
        self.strategy = self.create_strategy_inner()
        self.strategy.initialize_bot_stats()

        self.log_file = bot_settings.LEARN_LOG_FILE_CM

        if self.log_file is not None:
            str2w = "STARTING TO LEARN\nguesser is: " + tm_type + '\n\n'
            self.log_file.write(str2w)
        

    def create_strategy_inner(self):
        if self.learning_algorithm == LearningAlgorithms.T3:
            return StrategyThree(self)
        elif self.learning_algorithm == LearningAlgorithms.T4:
            return StrategyFour(self)

    def generate_clue(self, player_words, prev_clues, opponent_words, assassin_word, bystander_words):
        self.total_rounds += 1

        self.player_words = player_words
        self.opponent_words = opponent_words
        self.bystander_words = bystander_words
        self.assassin_word = assassin_word


        self.generate_all_bot_clues(player_words, prev_clues, opponent_words, assassin_word, bystander_words)

        #Before we select a bot, we need to update the values from last turn
        self.strategy.update_values()

        self.bot_to_use = self.strategy.select_bot()
        clue, targets = self.bot_clues_generated[self.bot_to_use]

        self.determine_contributing_bots(clue)

        self.log_round(self.bot_to_use)

        return clue, targets

    def give_feedback(self, guess, end_status):

        #if end_status is 0, game hasn't ended. 1 = loss and 2 = win

        self.add_consequences(guess)

        match(end_status):
            case GameCondition.LOSS: bot_str = f"\nend_status: loss\n\n"
            case GameCondition.WIN: bot_str = f"\nend_status: win\n\n"
            case GameCondition.CONTINUE if self.learning_algorithm == LearningAlgorithms.T3: bot_str = "\n"
            case _: bot_str = ""

        if self.bot_settings.PRINT_LEARNING:
            print(bot_str)
        if self.log_file is not None: self.log_file.write(bot_str)

    ###__________________________HELPER FUNCTIONS________________________###

    def add_consequences(self, guess):
        if guess in self.player_words:
            self.strategy.add_correct_consequence()
        elif guess in self.bystander_words:
            self.strategy.add_bystander_consequence()
        elif guess in self.opponent_words:
            self.strategy.add_opponent_consequence()
        else:
            self.strategy.add_assassin_consequence()

    def generate_all_bot_clues(self, player_words, prev_clues, opponent_words, assassin_word, bystander_words):
        for bot_type, bot in zip(self.bot_types, self.bots):
            self.bot_clues_generated[bot_type] = bot.generate_clue(player_words, prev_clues, opponent_words, assassin_word, bystander_words)

    def determine_contributing_bots(self, clue):
        #see what bots generated the clue
        self.bots_used.clear()
        for bot_type in self.bot_clues_generated: 
            if clue == self._get_bot_clue(bot_type):
                #Update bot streaks
                self.bots_used[bot_type] = 1
                self.usage_dict[bot_type] += 1

    def _get_bot_clue(self, bot_type):
        return self.bot_clues_generated[bot_type][0]
    
    ###__________________________LOGGER FUNCTIONS________________________###

    def get_bot_clues_generated(self):
        return ''.join(f"{bot}: {self._get_bot_clue(bot)}\n" for bot in self.bot_clues_generated.keys())
    
    def get_bot_weights(self):
        return ''.join(f"{bot}: {self.bot_weights[bot]}\n" for bot in self.bot_weights.keys())

    def log_round(self, bot_to_use):
        if self.log_file is not None:
            str2w = (
                f"BOT SELECTION STAGE\n"
                f"bot clues:\n{self.get_bot_clues_generated()}\n"
                f"UCB Constant: {self.ucb_constant}\n"
                f"bot weights:\n{self.get_bot_weights()}\n"
                f"chosen bot: {bot_to_use}\n\n"
                f"FEEDBACK STAGE\n"
            )

            if self.bot_settings.PRINT_LEARNING:
                print(str2w)
            
            if self.log_file != None: self.log_file.write(str2w)
    
    exceptions = ('log_file', "bot_settings")
    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo) if k not in self.exceptions else None)
        return result
