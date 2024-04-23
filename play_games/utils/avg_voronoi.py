if __name__ == "__main__":
    import sys, pathlib
    sys.path.append(pathlib.Path(__file__).parents[2].__str__())

from collections import Counter
import json
import os
import numpy as np
from play_games.bots.ai_components.associator_ai_components.associator_data_cache import AssociatorDataCache
from play_games.bots.ai_components.associator_ai_components.vector_data_cache import VectorDataCache
from play_games.paths import bot_paths
from play_games.bots.ai_components import vector_utils
from multiprocessing import Pool

SPLIT = 500
FOLDER = "voronoi"

def generate_voronoi():
    files = os.listdir(FOLDER)

    with open(files[0], "r") as f:
        data = json.load(f)

    for file in files[1:]:
        with open(files[0], "r") as f:
            temp = json.load(f)
        
        for lm, v in temp.items():
            for noise, words in v.items():
                data[lm][noise].update(words)

    with open("voronoi.json", "w") as f:
        json.dump(data, f)

if __name__ == "__main__":
    generate_voronoi()