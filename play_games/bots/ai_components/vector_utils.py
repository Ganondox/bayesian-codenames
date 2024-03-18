import numpy as np
from json import load

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
    noisy_embeddings = np.random.normal(clue_emb, std, (k, len(clue_emb)))
    def get_normal(x):
        return np.linalg.norm(noisy_embeddings-x, axis=1)
    distances = np.apply_along_axis(get_normal, 1, embeddings)
    
    return embeddings, distances