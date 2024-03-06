import numpy as np
from json import load
from scipy.spatial import distance as dist

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
    if len(wordvecs) == 0: return concatenated
    for vec in wordvecs[1:]:
        concatenated = np.hstack((concatenated, vec[word]))
    return concatenated

def perturb_embedding(v, std):
    """Accepts an embedding and applies a noise to it
    
    The Function used it gaussian multiplied by the length. In essence from 
    random unit vector 'r':   X = |v| + r * N(0, std)
    """
    if not std or std == 0:
        return v
    result = np.random.normal(size=v.shape)
    result = result / np.linalg.norm(result)
    
    #result = result * std * np.linalg.norm(v) # Rim
    result = result * np.sqrt(np.random.random()) * std * np.linalg.norm(v) # Uniform
    #result = result * np.random.normal(0, std) * np.linalg.norm(v) # Centrally distributed


    return result + v

def perturb_distance(dist, std):
    """Accepts a distance and applies a noise to it
    
    The Function used is Gaussian. X = dist + N(0, std).
    """
    if not std or std == 0:
        return dist
    result = dist + np.random.normal(0, std)
    #result = dist + np.random.random() * std # Uniform

    return result

def frequency(word, critical=1667):
    if word not in _frequencies: return -1
    frequency = _frequencies[word]
    if frequency > critical:
        return -1
    else:
        return -1/frequency

def dict_score(word1, word2):
    return dist.cosine(_d2v_embeddings[word1],_d2v_embeddings[word2])

def get_detect_score(clue: str, badwords = None, redwords = None, lambda_f = 2, lambda_d = 2):
    freq = lambda_f * frequency(clue)
    
    if redwords == badwords == None:
        return freq
    sum_red = np.sum([(1-dict_score(clue, word)) for word in redwords])
    min_bad = max([(1-dict_score(clue, word)) for word in badwords]) 
    
    return freq + lambda_d * (sum_red - min_bad)

_d2v_embeddings = load_vectors(file_paths.d2v_path)
with open(file_paths.freq_path) as f:_frequencies:dict[str, int] = load(f)