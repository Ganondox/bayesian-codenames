if __name__ == "__main__":
    import sys, pathlib
    sys.path.append(pathlib.Path(__file__).parents[2].__str__())

from collections import Counter
import json
import numpy as np
from play_games.bots.ai_components.associator_ai_components.associator_data_cache import AssociatorDataCache
from play_games.bots.ai_components.associator_ai_components.vector_data_cache import VectorDataCache
from play_games.paths import bot_paths
from play_games.bots.ai_components import vector_utils
from multiprocessing import Pool

def noisy(w, words, vecs,  vectors, noise):
    if noisy == 0: return w
    vec = vector_utils.perturb_embedding(vectors[w], noise)
    distances = np.linalg.norm(vecs-vec, axis=1)
    return words[distances.argmin()]

def get_lm_data(lm, noise, samples):
    lm_data = {}
    vec_path, assoc_path = bot_paths.get_vector_path_for_lm(lm), bot_paths.get_association_path_for_lm(lm)
    if isinstance(vec_path, (tuple, list)):
        vectors = VectorDataCache(*vec_path)
    else:
        vectors = VectorDataCache(vec_path)
    assocs = AssociatorDataCache(assoc_path)
    assocs.load_cache(500)
    # words = list(vectors)
    # vecs = np.array([vectors[a] for a in words])
    print(lm)
    for i, w in enumerate(vectors):
        count = {}
        words = assocs[w]
        vecs = np.array([vectors[a] for a in words])
        print(i)
        if noise != 0:
            _, distances = vector_utils.get_perturbed_euclid_distances(vectors[w], vecs, noise, samples)
            ids = np.argmin(distances, axis=1)
            count = Counter(np.take(words, ids).tolist())
            count = {k:v/samples for k,v in count.items()}
        else:
            count = {w: 1}
        lm_data[w] = count

    return lm_data


def generate_voronoi(lms, noise, *, verbose = False):
    SAMPLES = 1000
    with Pool(8) as pool:
        result = {}
        for lm, data in zip(lms, pool.starmap(get_lm_data, [ (lm, noise, SAMPLES) for lm in lms])):
            result[lm] = data
    return result

if __name__ == "__main__":
    from play_games.bots.types import LMType
    LMS = [LMType.W2V, LMType.GLOVE_50, LMType.GLOVE_100, LMType.GLOVE_200, LMType.GLOVE_300, LMType.CN_NB, LMType.D2V, LMType.FAST_TEXT, LMType.W2V_GLOVE_50, LMType.ELMO]
    # "w2v distance associator", "glove 300 distance associator", "cn_nb distance associator", "d2v distance associator", "fast-text distance associator",
    #             "glove 100 distance associator", "glove 200 distance associator", "w2v_glove distance associator", "elmo distance associator"
    noises = [0, 0.25, 0.5, 0.75, 1]  
    results = {}

    for noise in noises:  
        data = generate_voronoi(LMS, noise, verbose=True)
        for lm in data:
            results.setdefault(lm, {})[noise] = data[lm]

    with open("Voronoi.json", "w") as f:
        json.dump(results, f)