"""
This file does the actual game simulation and logs the stats and returns some to run_n_games. 

authors: Kim et al., Spencer Brosnahan, and Dallin Hunter
"""

import random
import time
from typing import TextIO
from play_games.bots.codemasters.codemaster import Codemaster
from play_games.bots.guessers.guesser import Guesser
from play_games.bots.types import BotType
from play_games.games.enums import Color, GameCondition

NUM_TEAM = 9
NUM_OPPONENT = 8
NUM_BYST = 7
NUM_ASSA = 1

class Game:
    """Class that setups up game details and calls Guesser/Codemaster pair to play the game
    """
    board_words: list[str]
    key_grid: list[Color]
    marked_words: list[bool]

    red_words: list[str]
    blue_words: list[str]
    bystander_words: list[str]
    assassin_word: str

    previous_guesses: set[str]
    clues_used: set[str]
    
    def __init__(self, btype1: BotType, btype2: BotType, codemaster: Codemaster, guesser: Guesser, board_words, seed, outfile:TextIO, print_boards=False):
        self.btype1 = btype1
        self.btype2 = btype2
        self.codemaster = codemaster
        self.guesser = guesser
        self.outfile = outfile
        self.do_print = print_boards
        self.game_start_time = time.time()
        random.seed(seed)

        self.assign_words(board_words)
        self._log_initial_message(seed)
        

    def assign_words(self, words):
        colors = [Color.TEAM] * NUM_TEAM + [Color.OPPONENT] * NUM_OPPONENT + [Color.BYST] * NUM_BYST + [Color.ASSA]
        zipped = list(zip(words, colors))
        random.shuffle(zipped)

        self.board_words, self.key_grid = zip(*zipped)
        self.marked_words = [False]*25

        self.red_words = words[:9]
        self.blue_words = words[9:17]
        self.bystander_words = words[17:24]
        self.assassin_word = words[24]

        self.previous_guesses = set()
        self.clues_used = set()

    def run(self):
        """Function that runs the codenames game between codemaster and guesser"""
        game_condition = GameCondition.CONTINUE
        round = 0
 
        while game_condition == GameCondition.CONTINUE:
            # # Creating game that will run only once clue/guess pair
            round += 1

            # board setup and display
            self.outfile.write(
                f"round: {round}\n"
                f"red_words_left: {list(self.red_words)}\n"
                f"blue_words_left: {list(self.blue_words)}\n"
                f"bystander_words_left: {list(self.bystander_words)}\n"
                f"assassin_word: {self.assassin_word}\n"
                f"num_red_words_left: {len(self.red_words)}\n"
            )

            # codemaster gives clue & number here
            clue, clue_num = self._get_codemaster_clue()
            guesses = self._get_guesser_guesses(clue, clue_num)

            for guess_num, guess_answer in enumerate(guesses[:clue_num], 1):
                guess_answer = guess_answer.lower().strip()
                guess_answer_index = self.board_words.index(guess_answer)
                color_guessed = self.key_grid[guess_answer_index]

                self.outfile.write(f"guess: {guess_answer}\n")
                game_condition = self._accept_guess(guess_answer_index, guess_answer)
                self._give_bots_feedback(game_condition, guess_answer, color_guessed)
                self._display_board_codemaster()

                if game_condition != GameCondition.CONTINUE: 
                    self.game_end_time = time.time()
                if color_guessed != Color.TEAM: 
                    break
                
            self.outfile.write(f"num_actual_guesses: {guess_num}\n")
            self.outfile.write('\n')
        self.outfile.write('\n')

    def _log_initial_message(self, seed):
        game_string = f"CODEMASTER: {self._get_bot_descr(self.btype1, self.codemaster)}\nGUESSER: {self._get_bot_descr(self.btype2, self.guesser)}\n"
        self.outfile.write(game_string)
        self._display_board_codemaster()
        self.outfile.write(f"seed: {seed}\n")
        self.outfile.write("board_words: " + str(self.board_words) + '\n\n')

    def _get_word_repr(self, index): 
        if self.marked_words[index]:
            return ("*Red*", "*Blue*", "*Bystander*", "*Assassin*")[self.key_grid[index]]
        else:
            return self.board_words[index]
    
    def _display_board_codemaster(self):
        """prints out board with color-paired words, only for codemaster, color && stylistic"""
        if self.do_print:
            print(str.center("BOARD", 79, '_')+'\n', file=self.outfile)
            for counter in range(len(self.board_words)):
                if counter >= 1 and counter % 5 == 0: print("\n", file=self.outfile)
                print(str.center(self._get_word_repr(counter), 15), " ", end ='', file=self.outfile)
            print(f"\n{'_'*79}\n", file=self.outfile)

    def _accept_guess(self, guess_index, guess):
        """Function that takes in an int index called guess to compare with the key grid
        CodeMaster will always win with Red and lose if Blue =/= 7 or Assassin == 1

        1 loss, 2 win, 0 continue
        0 red, 1 blue, 2 bystander, 3 assassin
        first end status, second word type
        """
        self.marked_words[guess_index] = True
        color_guessed = self.key_grid[guess_index]
        self.previous_guesses.add(guess)
        condition = GameCondition.CONTINUE
        
        match color_guessed:
            case Color.TEAM:
                self.red_words.remove(guess)
                self.outfile.write("correct guess\n")
            case Color.OPPONENT:
                self.blue_words.remove(guess)
                self.outfile.write("incorrect guess\n")
            case Color.ASSA:
                self.outfile.write("assassin guessed\n")
            case Color.BYST:
                self.bystander_words.remove(guess)
                self.outfile.write("bystander guessed\n")
        
        if len(self.red_words) <= 0:
            self.outfile.write("game won\n")
            condition = GameCondition.WIN 
        elif color_guessed == Color.ASSA or len(self.blue_words) <= 0:
            self.outfile.write("game lost\n")
            condition = GameCondition.LOSS
        
        return condition
        
    def _give_bots_feedback(self, status, guess, color):
        self.codemaster.give_feedback(guess, status)
        self.guesser.give_feedback(status, color)

    def _get_bot_descr(self, bot_type, bot_inst):
        return bot_type if not hasattr(bot_inst, '__desc__') else bot_inst.__desc__()

    def _get_codemaster_clue(self):
        clue_giving_start = time.time()
        clue, targets = self.codemaster.generate_clue(self.red_words[:], self.clues_used.copy(), self.blue_words[:], self.assassin_word,  self.bystander_words[:])                                                   
        self.outfile.write(f"clue: {clue}\ntargets: {targets}\nnum_targets: {len(targets)}\n")        
        self.clues_used.add(clue)
        clue_giving_time = time.time() - clue_giving_start
        self.outfile.write(f"clue_generation_time: {clue_giving_time}\n")

        return clue, len(targets)

    def _get_guesser_guesses(self, clue, clue_num):
        guessing_start = time.time()
        guesses = self.guesser.guess_clue(clue, clue_num, self.previous_guesses)
        self.outfile.write(f"guesses: {guesses}\n")
        guessing_time = time.time() - guessing_start
        self.outfile.write(f"guess_generation_time: {guessing_time}\n")

        return guesses

    