import matplotlib.pyplot as plt
import numpy as np
import json
import os
from play_games.utils import utils
from play_games.bots.types.bot_to_ai import get_ai
from bots.types import AIType

#These are keys that are found in the round files so we can pick out the values that we want.
class RoundParseKeys:
    SPYMASTER = "SPYMASTER"
    GUESSER = "GUESSER"
    ROUND = "round"
    GUESS = "guess"
    GAME_LOST = "game lost"
    GAME_WON = "game won"
    CORRECT = "correct guess"
    BLUE = "incorrect guess"
    BYSTANDER = "bystander guessed"
    ASSASSIN = "assassin guessed"
    N_TARGETS = "num_targets"
    #These are used for starting a game at a certain state
    SEED = "seed"
    BOARD_WORDS = "board_words"
    RED_WORDS_LEFT = "red_words_left"
    BLUE_WORDS_LEFT = "blue_words_left"
    BYSTANDER_WORDS_LEFT = "bystander_words_left"
    ASSASSIN_WORD = "assassin_word"
    NUM_RED_WORDS_LEFT = "num_red_words_left"
    CLUE = "clue"
    TARGETS = "targets"
    GUESSES = "guesses"

class LearnParseKeys:
    START_TOKEN = "STARTING TO LEARN"
    CURR_TEAM_MATE_TOKEN = "GUESSER"
    CHOSEN_BOT_TOKEN = 'chosen bot'
    BOT_WEIGHTS_TOKEN = 'bot weights:'
    END_TOKEN = 'end_status'

class CompiledDataKeys:
    STAT_COMPARISON = "Stat Comparison"
    ARM_WEIGHTS = "Arm Weights"
    PERCENTAGES = "Arm Percentages"
    PERF_PROG = "Performance Progression"
    PERF_PROG_SLIDE = "Performance Progression Sliding Window"
    FINAL_STAT_DIST = "Final Stat Distributions"


class Types:
    CM = 0
    G = 1


class Stats: #ALL stats that will be used for graphing and for stat dict creation

    #KEYS FOR DATA GATHERING PHASE
    RED_WORDS_FLIPPED_BY_ROUND = "Red Words Flipped By Round"
    BLUE_WORDS_FLIPPED_BY_ROUND = "Blue Words Flipped By Round"
    BYSTANDER_WORDS_FLIPPED_BY_ROUND = "Bystander Words Flipped By Round"
    ASSASSIN_WORDS_FLIPPED_BY_ROUND = "Assassin Words Flipped By Round"
    NUM_ROUNDS_PER_GAME = "Number of Rounds Per Game" 
    GAME_WIN_LOSS = "Game Win Loss" 
    CLUE_NUM_BY_ROUND = "Clue Number Given By Round"
    POSTERIORS_BY_ROUND = "Posteriors By Round"
    '''
    These are for learning experiments
    '''

    #KEYS FOR DATA PROCESSING (Use the keys for data gathering to access the saved dictionary and save data to a new dictionary)
    WIN_RATE = "Win Rate"
    AVG_WIN_TIME = "Average Win Time"
    AVG_TURNS_BY_GAME = "Average Turns By Game"
    TURNS_BY_GAME = "Turns By Game"
    AVG_RED_FLIP_BY_GAME = "Average Red Words Flipped By Game"
    AVG_BLUE_FLIP_BY_GAME = "Average Blue Words Flipped By Game"
    AVG_BYSTANDER_FLIP_BY_GAME = "Average Bystander Words Flipped By Game"
    AVG_ASSASSIN_FLIP_BY_GAME = "Average Assassin Words Flipped By Game"
    RED_FLIP_BY_GAME = "Red Words Flipped By Game"
    BLUE_FLIP_BY_GAME = "Blue Words Flipped By Game"
    BYSTANDER_FLIP_BY_GAME = "Bystander Words Flipped By Game"
    ASSASSIN_FLIP_BY_GAME = "Assassin Words Flipped By Game"

class StatDictKeys: 
    G_LEARN_STATS = "Guesser Learning Stats"
    CM_LEARN_STATS = "Spymaster Learning Stats"
    FINAL_KEY = "Final"
    BEST_AVG = "Best Average"
    AVG_PERF = "Average Performance"
    BEST_OVERALL = "Best Overall"
    SPYMASTER = "Spymaster"
    GUESSER = "Guesser"
    SOLO_BOT_DATA = "Solo Bot Data"
    RANDOM = "Random"


COMPILED_DATA_STATS = [Stats.WIN_RATE, \
                            Stats.AVG_WIN_TIME,]
#These are the stat keys we use for graphing. They are the same as the bread and butter stats
MAIN_STATS_KEYS = [Stats.WIN_RATE, Stats.AVG_WIN_TIME, Stats.AVG_TURNS_BY_GAME, Stats.TURNS_BY_GAME, Stats.AVG_RED_FLIP_BY_GAME, Stats.AVG_BLUE_FLIP_BY_GAME, Stats.AVG_BYSTANDER_FLIP_BY_GAME, 
    Stats.AVG_ASSASSIN_FLIP_BY_GAME,]


def load_dict(bests_json_path):
    best_team_mates = {}
    with open(bests_json_path) as f:
        best_team_mates = json.load(f)
    return best_team_mates

def save_json(json_obj, save_path):
    utils.create_path(save_path)
    with open(save_path, 'w+') as f:
        json.dump(json_obj, f)

def load_json(filepath):
    with open(filepath, 'r') as f:
        json_obj = json.load(f)
    return json_obj

def extract_val(val):
    if isinstance(val, (tuple, list)):
        return val[0]
    return val