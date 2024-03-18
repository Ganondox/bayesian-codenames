from pathlib import Path
import sys
import time

from play_games.utils import utils

__root = Path(__file__).parent

sys.path.insert(0, str(__root.parents[3])) 


import itertools
import os

from matplotlib import pyplot as plt
import pandas as pd
import random
import numpy as np

from multiprocessing import Pool

from play_games.ai_components.vector_baseline_components.vector_utils import VectorUtils
from play_games.spymasters.noisy_distance_associator_spymaster import NoisyDistanceAssociatorAISpymaster
from play_games.utils.bot_parameter_settings import BotPaths
from play_games.utils.bot_settings_obj import BotSettingsObj
from play_games.utils.file_paths_obj import FilePathsObj
from play_games.utils.object_manager import ObjectManager as Manage

from play_games.utils.utils import BotTypes
from play_games.utils.bot_initializer import BotInitializer as Init
obj = Manage()
words = utils.load_word_list(None, obj.file_paths_obj.board_words_path)


bot_paths = BotPaths(BotTypes(), FilePathsObj())

def get_bot_settings(b_type):
    bot_settings = BotSettingsObj()
    bot_settings.N_ASSOCIATIONS = 300
    bot_settings.CONSTRUCTOR_PATHS = bot_paths.get_paths_for_bot(b_type)
    bot_settings.MODEL_PATH = FilePathsObj.model_path
    bot_settings.BOT_TYPE_SM = b_type
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

def gather_data(assoc, bot, n_repl, seed):
    b_settings = get_bot_settings(bot)
    b_settings.N_ASSOCIATIONS = int(assoc)
    b_settings.DETECT = (2,2)
    normal_cm, *_ = obj.bot_initializer.init_bots(bot, None, b_settings)
    
    data = []

    start_t = time.time()
    for i in range(n_repl):
        random.seed(seed+i)
        team_words, opponent_words, byst_words, assasin, board = get_random_board()
        normal_cm.load_dict(board)

        _, normal_targets = normal_cm.generate_clue(team_words, [], opponent_words, assasin, byst_words)

        data.append(len(normal_targets))
    print(assoc, bot, n_repl, seed, (time.time() - start_t)/n_repl)
    return assoc, bot, data

def save_plots_and_graph(data, n_label, x_label, y_label):
    print(data)
    N = set()
    X = set()

    for n, rest in data.items():
        N.add(n)
        for x in rest:
            X.add(x)
    N = sorted(N)
    X = sorted(X)

    table = np.ndarray((len(N), len(X)), float)

    for (n_i, n_v), (x_i, x_v) in itertools.product(enumerate(N), enumerate(X)):
        if not(n_v in data and x_v in data[n_v]):
            table[n_i][x_i] = 0
            continue

        table[n_i][x_i] = data[n_v][x_v]

    for n_i, n_v in enumerate(N):
        plt.plot(X, table[n_i], label=n_v)

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend(title=n_label)
    plt.savefig(f"{n_label}-{x_label}-{y_label}.png")
    plt.show()
  
    pd.DataFrame(table, index=N, columns=X).to_csv(f"{n_label}-{x_label}-{y_label}.csv")


def run_tests(n_assoc_vals, bot_vals, n_repl, seed=20):

    results = {}
    pool = Pool(processes=12)
    print("GATHERING DATA")
    m = pool.starmap(gather_data, map(lambda v: (*v, n_repl, seed), itertools.product(n_assoc_vals, bot_vals)))
    # (N, X, Y)
    average_per_bot = {}
    frequencies = {}

    print("ORGANIZING DATA")
    for assoc, bot, results in m:
        average_per_bot.setdefault(bot, {}).setdefault(assoc, []).extend(results)
        frequencies.setdefault(assoc, []).extend(results)
    

    frequency_per_size = {}
    for assoc, results in frequencies.items():
        unique, count = np.unique(results, return_counts=True)
        suma = sum(count)
        for un, c in zip(unique, count):
            if assoc not in frequency_per_size.setdefault(un, {}): 
                frequency_per_size[un][assoc] = 0
            frequency_per_size.setdefault(un, {})[assoc] = c/suma
    
    for bot, results in average_per_bot.items():
        for assoc in results:
            results[assoc] = np.average(results[assoc])

    print("MAKING PLOTS")

    os.makedirs("DATA_PLOTS", exist_ok=True)
    os.chdir("DATA_PLOTS")
    save_plots_and_graph(frequency_per_size, "Clue Size", "# Associations", "Frequency")
    save_plots_and_graph(average_per_bot, "Bot Type", "N_Associations", "Average Clue Size")
    
    print("FINSISHED")


if __name__ == '__main__':

    N_ASSOC_VALS = [int(v) for v in np.linspace(50, 300, 6)]
    BOT_VALS = [BotTypes.BERT1_DISTANCE_ASSOCIATOR, BotTypes.BERT2_DISTANCE_ASSOCIATOR, BotTypes.ELMO_DISTANCE_ASSOCIATOR, BotTypes.W2V_DISTANCE_ASSOCIATOR, BotTypes.W2V_GLOVE_DISTANCE_ASSOCIATOR,
                BotTypes.GLOVE_200_DISTANCE_ASSOCIATOR, BotTypes.CN_NB_DISTANCE_ASSOCIATOR, BotTypes.D2V_DISTANCE_ASSOCIATOR]
    N_REPL = 1000
    SEED = 0

    run_tests(N_ASSOC_VALS, BOT_VALS, N_REPL, SEED)
