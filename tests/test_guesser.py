from datetime import timedelta
from enum import IntEnum, StrEnum
import os

import numpy as np
from pathlib import Path
import sys


__root = Path(__file__).parent

sys.path.insert(0, str(__root.parents[0])) 

from play_games.bots.types.bot_to_lm import get_lm

import sys
import time

import random
from play_games.games.enums import Color
from play_games.utils import utils
from play_games.bots.types import BotType, AIType, LMType
from play_games.paths import bot_paths, file_paths
from play_games.bots.bot_settings_obj import BotSettingsObj
from play_games.utils.object_manager import ObjectManager as Manage

"""
If running from the terminal, optionally add arguments
See Defaults below

Fixed_ Strategy
argv[1] gets set to num games
argv[2] gets set to seed, or "True" sets "None" for seed (random seed)
argv[3] represents index in codemasters to try (see below: mastersToTry)
argv[4] represents index in guessers to try (see below: guessersToTry)
argv[5] represents weight
argv[6] represents threshold

"""

obj = Manage()
words = utils.load_word_list(file_paths.board_words_path)

# DEFAULT VALUES
GAMES_TO_PLAY = 50
SEED = 2050
CODEMASTER = BotType.D2V_DISTANCE_ASSOCIATOR
N_GUESSER = BotType.W2V_BASELINE_GUESSER
GUESSER = BotType.W2V_BASELINE_GUESSER

def main():
    random.seed(SEED)
    bot_settings = get_bot_settings(CODEMASTER)
    bot_settings.BOT_TYPE_G = get_lm(N_GUESSER)
    bot_settings.EMBEDDING_NOISE = 0
    bayes, test_g = obj.bot_initializer.init_bots(CODEMASTER, BotType.NOISY_GUESSER, bot_settings)

    bot_settings = get_bot_settings(CODEMASTER)
    _, baseline_g = obj.bot_initializer.init_bots(None, GUESSER, bot_settings)

    games_played = 0
    win = 0
    while(games_played < GAMES_TO_PLAY):
        t_game_start = time.time()
        random.seed(SEED + games_played)
        print(f"_______________________ Game {games_played+1} ____________________________")
        team_words, opponent_words, byst_words, assasin, board = get_random_board()
        print_board(team_words, opponent_words, byst_words, assasin, board)

        bayes.load_dict(board)
        test_g.load_dict(board)
        baseline_g.load_dict(board)

        
        prev_guesses=[]
        state = GameState.ROUND_END
        round_ = 1
        
        while(state == GameState.ROUND_END):
            color = Color.TEAM
            print("Round", round_) 
            random.seed(SEED + games_played*100+round_)
            np.random.seed(SEED + games_played*100+round_)
            clue, targets = bayes.generate_clue(team_words, prev_guesses, opponent_words, assasin, byst_words)
            np.random.seed(SEED + games_played*100+round_)
            random.seed(SEED + games_played*100+round_)


            print("CODEMASTER: ", clue, get_colored_list(targets,team_words, opponent_words, byst_words, assasin))
            guesses = test_g.guess_clue(clue, len(targets), prev_guesses)
            print("TEST GUESSER: ", get_colored_list(guesses, team_words, opponent_words, byst_words, assasin))

            baseline_guesses = baseline_g.guess_clue(clue, len(targets), prev_guesses)
            print("TEST GUESSER: ", get_colored_list(baseline_guesses, team_words, opponent_words, byst_words, assasin))
            for i, guess in enumerate(guesses, 1):
                
                if guess in team_words:
                    color = Color.TEAM
                    team_words.remove(guess)
                elif guess in opponent_words:
                    color = Color.OPPONENT
                    opponent_words.remove(guess)
                elif guess in byst_words:
                    color = Color.BYSTANDER
                    byst_words.remove(guess)
                elif guess == assasin:
                    color = Color.ASSASSIN
                prev_guesses.append(guess)
                
                bayes.give_feedback(guess, color, 0)
                print("  ", guess, ":", color)
                if color != Color.TEAM:
                    break
            round_+=1
            if color == Color.ASSASSIN or len([v for v in opponent_words if v not in prev_guesses]) == 0:
                state = GameState.LOSE
            if len([v for v in team_words if v not in prev_guesses]) == 0:
                state = GameState.WIN
                win+=1
        print(state)
        games_played+=1
        t_game_end = time.time()
        print(f"Time Elapsed: {timedelta(seconds=t_game_end-t_game_start)}")

        print(win, games_played, round(win/games_played, 2))



def get_bot_settings(b_type):
    bot_settings = BotSettingsObj()
    bot_settings.N_ASSOCIATIONS = 500
    bot_settings.CONSTRUCTOR_PATHS = bot_paths.get_paths_for_bot(b_type)
    bot_settings.BOT_TYPE_SM = b_type
    #bot_settings.LOG_FILE = file_paths.anc_log_path

    if len(sys.argv) > 1:
        try:
            global GAMES_TO_PLAY
            GAMES_TO_PLAY = int(sys.argv[1])
        except:
            pass
        print(f"Playing {GAMES_TO_PLAY} games")
    if len(sys.argv) > 2:
        global SEED
        if sys.argv[2].lower() == "true":
            SEED = None
        else:
            try:
                SEED = int(sys.argv[2])
                bot_settings.TEST_ID = SEED
            except:
                pass # default set above
        print(f"Seed and test ID: {SEED}")

    mastersToTry = [BotType.W2V_GLOVE_DISTANCE_ASSOCIATOR]
    guessersToTry = [BotType.W2V_GLOVE_BASELINE_GUESSER, BotType.W2V_BASELINE_GUESSER, BotType.GLOVE_50_BASELINE_GUESSER,
                     BotType.GLOVE_100_BASELINE_GUESSER, BotType.CN_NB_BASELINE_GUESSER, BotType.D2V_BASELINE_GUESSER,
                     BotType.ELMO_BASELINE_GUESSER, BotType.FAST_TEXT_BASELINE_GUESSER, BotType.BERT1_BASELINE_GUESSER]

    if len(sys.argv) > 4:
        try:
            global CODEMASTER
            global GUESSER
            CODEMASTER = mastersToTry[int(sys.argv[3])]
            GUESSER = guessersToTry[int(sys.argv[4])]
        except:
            print(f"Invalid Master/Guesser Index Value")
            pass
        print(f"Using Master: {CODEMASTER}, Guesser: {GUESSER}")

    # Note: not every bot has a weight

    return bot_settings

def get_random_board():
    board = random.sample(words, 25)
    random.shuffle(board)
    team_words = board[:9]
    opponent_words = board[9:17]
    byst_words = board[17:24]
    assasin = board[24]
    random.shuffle(board)

    return team_words, opponent_words, byst_words, assasin, board

def print_board(team_words, opponent_words, byst_words, assasin, board):
    for i in range(5):
        for j in range(5):
            string = ""
            word = board[i*5+j]
            if word in team_words: string += '\u001b[31m'
            elif word in opponent_words: string += '\u001b[34m'
            elif word in byst_words: string += '\u001b[90m'
            else: string+='\u001b[0m'
            string+=word
            print(f"{string:<20}", end=" ")
        print('\u001b[0m')
    print()

def color_word(word, team_words, opponent_words, byst_words, assasin):
    string = ""
    if word in team_words: string += '\u001b[31m'
    elif word in opponent_words: string += '\u001b[34m'
    elif word in byst_words: string += '\u001b[90m'
    else: string+='\u001b[0m'
    string+=word+'\u001b[0m'

    return string

def get_colored_list(words, team_words, opponent_words, byst_words, assasin):
    return "["+",".join([color_word(word, team_words, opponent_words, byst_words, assasin) for word in words])+"]"

class GameState(StrEnum):
    WIN="GAME WON"
    LOSE="GAME LOST"
    ROUND_END="NONE"

if __name__ == '__main__':
    main()