import bisect
import scipy.spatial.distance as dist
import numpy as np
from json import load, dump 

def generate(output_path, model_path, words_path, n=300, verbose=False):
    vectors = load_lm(model_path)
    if verbose: print("Parsed Embeddings")
    words = load_words(words_path)
    if verbose: print("Loaded Words... Starting generation")

    associations = gen_association(vectors, words, n=n, verbose=verbose)

    with open(output_path, "w") as f:
        dump(associations, f)

    return associations

# txt files are actually faster to parse
def txt_to_json(output_path, model_path):
    '''To convert txt to json embeddings'''
    vectors = load_lm(model_path)
    with open(output, "w") as f:
        dump(vectors, f)

def vec_to_txt(output_path, model_path, words_path):
    '''To convert txt to json embeddings'''
    words = set(load_words(words_path))
    new_words = set()
    import codecs

    with open(output_path, "w") as output: 
        with open(model_path, "r", encoding="utf-8") as input_:

            for line in input_:
                word = line.split(maxsplit=1)[0]
                if word in words:
                    new_words.add(word)
                    output.write(line.lower().strip())
                    output.write('\n')
    print(bool(words-new_words))

### HELPER FUNCTIONS ###
embeddings = dict[str, list[float]]

def load_lm(file_name: str) -> embeddings:
    with open(file_name, "r") as f:
        if(file_name [-3:] in ("txt", "vec")):
            vectors = dict()
            for line in f:
                ls = line.split()
                assert len(ls) > 1, "Can't read embeddings file"
                vectors[ls[0]] = [float(n) for n in ls[1:]]
            return vectors
        else:
            return {key:np.array(value) for key,value in load(f).items()}

def load_words(file_name: str) -> list[str]:
    lines = []
    with open(file_name, "r") as f:
        lines = [line.rstrip() for line in f]
    return lines

def gen_association(dist_dict: embeddings, board_word: list[str],n=300, verbose=False) -> dict[str, list[str]]:
    ret_dict = dict()
    all_dists = np.array([v for v in dist_dict.values()])
    __cache = {}

    for i, word in enumerate(board_word, start=1):
        dists = np.linalg.norm(all_dists-dist_dict[word], axis=1)
        for j, k in enumerate(dist_dict):
            bob  = (k, word) if k < word else (word, k)
            if bob not in __cache:
                __cache[bob] = dists[j]

        temp_associations = []
        for key in dist_dict:
            if(key == word): 
                continue

            bob  = (key, word) if key < word else (word, key)

            if bob not in __cache:
                __cache[bob] = dist.euclidean(dist_dict[word], dist_dict[key])  
            pair = (__cache[bob], key)
            temp_associations.append(pair)
        temp_associations.sort()
        if(len(temp_associations) > n): del temp_associations[n:] #trim to 300
        ret_dict[word] = [pair[1] for pair in temp_associations]
        if verbose: print(f"{i}/{len(board_word)}", end='\r')
    return ret_dict


def bin_search(obj, ls)->int:
    '''Find the index of the slot next to it's predesesor'''
    low = -1
    high = len(ls)
    ind = (low + high)//2

    if len(ls)==0: return 0
    
    while(low < high-1):
        if obj[1] == ls[ind][1]: return ind+1
        elif obj[1] > ls[ind][1]: low = ind
        else: high = ind

        ind = (low + high)//2
    return high

if __name__ == "__main__":
    lms = ['w2v', 'bert1', 'bert2', 'd2v', 'elmo','fast-text', 'glove_50', 'glove_100', 'glove_200', 'glove_300', 'w2v_glove']
    all_words = set()
    for lm in lms:
        vectors = fr"raw_data/{lm}_lm.txt"
        words = r"raw_data/actual-final-wl.txt" #r"raw_data/common_boardwords.txt"
        output = fr"data_objects/associator_objects/test/{lm}_final_boardwords_associations.json" 
        generate(output, vectors, words, n=500, verbose=True)
        # all_words.update(*generate(output, vectors, words, n=500, verbose=True).values())
        #txt_to_json(output, vectors)
    # with open("wl.txt", 'w') as f:
    #     f.write('\n'.join(list(all_words)))