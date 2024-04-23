'''
This file will contain associations from the json file. You will pass in a filepath
'''


from play_games.bots.ai_components import vector_utils as vutils
from scipy.spatial.distance import euclidean

__vectors_cache = dict()
__distance_cache = dict()

__dist_fn = euclidean # cosine

def distance_vec(vec1, vec2):
    return __dist_fn(vec1, vec2)

def _pull_vectors_from_cache(filepath):
    if filepath not in __vectors_cache:
        __vectors_cache[filepath] = vutils.load_vectors(filepath)
    return __vectors_cache[filepath]

def _get_distance_from_cache(key_file, w1, w2, vectors ):
    if key_file not in __distance_cache:
        __distance_cache[key_file] = dict()
    current_dict = __distance_cache[key_file]
    
    key_l = min(w1,w2)
    key_h = max(w1,w2)

    if key_l not in current_dict:
        current_dict[key_l] = dict()
    current_dict = current_dict[key_l]

    if key_h not in current_dict:
        current_dict[key_h] = __dist_fn(vutils.concatenate(w1, vectors), vutils.concatenate(w2, vectors))
    
    return __distance_cache[key_file][key_l][key_h]



class VectorDataCache:
    def __init__(self, *filepaths):
        self.filepaths = filepaths
        self.__key = "".join(filepaths)
        self.vectors = [_pull_vectors_from_cache(filepath) for filepath in filepaths]
        
    def vector(self, w):
        return vutils.concatenate(w, self.vectors)
    
    def values(self):
        for k in self:
            yield self.vector(k)

    def __getitem__(self, key):
        return self.vector(key)

    def __contains__(self, key):
        return key in self.vectors[0]
    
    def __iter__(self):
        yield from self.vectors[0].__iter__()
    
    def distance_word(self, w1, w2):
        return _get_distance_from_cache(self.__key, w1, w2, self.vectors)
    
    def __deepcopy__(self, _):
        return self