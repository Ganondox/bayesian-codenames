from copy import deepcopy
import random

#Bot libraries
from bots.ai_components.ensemble_ai_components.ensemble_ai import EnsambleAI
from bots.ai_components.ensemble_ai_components.ensemble_utils import LearningAlgorithms
from bots.ai_components.ensemble_ai_components.strategies import StrategyFour, StrategyThree
from bots.guessers.guesser import Guesser
from games.enums import Color, GameCondition


class EnsembleAIGuesser(EnsambleAI, Guesser):

    def __init__(self):
        random.seed(42)
        #After guess is decided on, these will be set so we can refer to them in the feedback stage
        self.curr_guesses = None

        #We will use bot_guesses_generated in order to determine the bots involved and then we'll put them in bots_used
        self.bot_guesses_generated = {}
        self.bots_used = {}
        self.bot_to_use = None

        #These help us decide which bots to select. Usage dict helps us to see which ones we haven't tried. 
        #bot weights is what we use to select the bot (Max or min value is chosen)
        self.usage_dict = {}
        self.bot_weights = {}

        self.total_rounds = 0


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

        self.log_file = bot_settings.LEARN_LOG_FILE_G

        if self.log_file is not None:
            str2w = "STARTING TO LEARN\ncodemaster is: " + tm_type + '\n\n'
            self.log_file.write(str2w)
        

    def create_strategy_inner(self):
        match self.learning_algorithm:
            case LearningAlgorithms.T3: 
                return StrategyThree(self)
            case LearningAlgorithms.T4: 
                return StrategyFour(self)

    def guess_clue(self, clue, num_guesses, prev_guesses):
        self.total_rounds += 1

        self.generate_all_bot_guesses(clue, num_guesses, prev_guesses)

        #Before we select a bot, we need to update the values from last turn
        self.strategy.update_values()

        self.bot_to_use = self.strategy.select_bot()
        guesses = self.bot_guesses_generated[self.bot_to_use]

        self.determine_contributing_bots(guesses)

        self.log_round(self.bot_to_use)

        self.curr_guesses = guesses

        return guesses

    def give_feedback(self, end_status: GameCondition, word_type: Color):

        #if end_status is 0, game hasn't ended. 1 = loss and 2 = win

        self.add_consequences(word_type)

        match(end_status):
            case 1: bot_str = f"\nend_status: loss\n\n"
            case 2: bot_str = f"\nend_status: win\n\n"
            case _: bot_str = "\n"

        if self.bot_settings.PRINT_LEARNING:
            print(bot_str)
        if self.log_file is not None: self.log_file.write(bot_str)

    ###__________________________HELPER FUNCTIONS________________________###

    def add_consequences(self, word_type):
        match word_type:
            case Color.TEAM:     self.strategy.add_correct_consequence()
            case Color.OPPONENT: self.strategy.add_opponent_consequence()
            case Color.BYST:     self.strategy.add_bystander_consequence()
            case Color.ASSA:     self.strategy.add_assassin_consequence()
    
    def generate_all_bot_guesses(self, clue, num_guesses, prev_guesses):
        for bot_type, bot in zip(self.bot_types, self.bots):
            self.bot_guesses_generated[bot_type] = bot.guess_clue(clue, num_guesses, prev_guesses)
        
    def determine_contributing_bots(self, guesses):
        #see what bots generated the clue
        self.bots_used.clear()
        for bot in self.bot_guesses_generated:
            curr_guesses = self.bot_guesses_generated[bot]
            #We add the percentage of guesses that a bot had the same
            same_guesses = [g for g in guesses if g in curr_guesses]
            percent_contribution = len(same_guesses) / len(guesses)
            if percent_contribution > 0:
                self.bots_used[bot] = percent_contribution
                self.usage_dict[bot] += percent_contribution

    ###__________________________LOGGER FUNCTIONS________________________###

    def get_bot_guesses_generated(self):
        bot_str = ''
        for key in self.bot_guesses_generated.keys():
            bot = key
            guesses = self.bot_guesses_generated[key]
            bot_str += bot + ": " + " ,".join(guesses) + '\n'

        return bot_str
    
    def get_bot_weights(self):
        return ''.join([f"{bot}: {weight}\n" for bot, weight in self.bot_weights.items()])

    def log_round(self, bot_to_use):
        if self.log_file is not None:
            str2w = (
                f"BOT SELECTION STAGE\n"
                f"bot clues:\n{self.get_bot_guesses_generated()}\n"
                f"UCB Constant: {self.ucb_constant}\n"
                f"bot weights:\n{self.get_bot_weights()}\n"
                f"chosen bot: {bot_to_use}\n\n"
                f"FEEDBACK STAGE\n"
            )

            if self.bot_settings.PRINT_LEARNING:
                print(str2w)
            if self.log_file != None: self.log_file.write(str2w)
    
    exceptions = {'log_file', "bot_settings"}
    def __deepcopy__(self, memo):

        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo) if k not in self.exceptions else None)
        return result