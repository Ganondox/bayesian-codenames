import numpy as np
from json import load
from play_games.paths import file_paths

def load_vectors(path:str):
    with open(path, "r", encoding="utf-8") as infile:
        if path[-3:] in ("txt", "vec"):
            vecs = {}
            for line in infile:
                line = line.rstrip().split()
                vecs[line[0]] = np.array(line[1:], dtype=float)
            return vecs
        elif path.endswith("json"):
            return {key:np.array(vector) for key,vector in load(infile).items()}

def concatenate(word, wordvecs): 
    concatenated = wordvecs[0][word]
    if len(wordvecs) == 0 or len(wordvecs) == 1: return concatenated
    for vec in wordvecs[1:]:
        concatenated = np.hstack((concatenated, vec[word]))
    return concatenated

def perturb_embedding(v, std):
    if not std or std == 0:
        return v
    return np.random.normal(v, std)

def get_perturbed_euclid_distances(clue_emb, embeddings, std, k):
    noisy_embeddings = np.random.normal(clue_emb, std, (k,len(clue_emb)))
    def get_normal(x):
        return np.linalg.norm(noisy_embeddings-x, axis=1)
    distances = np.apply_along_axis(get_normal, 1, embeddings)

    return noisy_embeddings, distances.T

def get_voronoi_distr(lm, word1, word2, noise):
    if noise not in VORONOI_STATS[lm]: return int(word1 == word2)
    return VORONOI_STATS[lm][noise][word1].get(word2, 0)

try:
    with open(file_paths.voronoi_stats_path, "r") as f:
        VORONOI_STATS = load(f)
        VORONOI_STATS = {k: {float(k2): v2 for k2, v2 in v.items()} for k,v in VORONOI_STATS.items()}
except:
    pass

if __name__ == "__main__":
    vectors = [v[:200] for v in load_vectors("./raw_data/w2v_lm.txt").values()]
    clue_emb = vectors[0]
    noisy_emb, opt = get_perturbed_euclid_distances(clue_emb, vectors, 0.2, 200)
    print(np.linalg.norm(noisy_emb, axis=1))
    save = []
    from scipy.spatial.distance import euclidean
    for emb in noisy_emb:
        save.append([np.linalg.norm(v-emb) for v in vectors])

    non = np.array(save)

    print(np.all(np.abs(non-opt) < 0.00000000001))

