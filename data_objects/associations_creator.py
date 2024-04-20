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
    __cache = {}
    for i, word in enumerate(board_word, start=1):
        temp_associations = []
        for key in dist_dict:
            if(key == word): 
                continue

            bob  = (key, word) if key < word else (word, key)

            if bob not in __cache:
                    
            pair = (key, dist.euclidean(dist_dict[word], dist_dict[key]))
            bisect.insort(temp_associations, pair, key=lambda x:x[1])
            if(len(temp_associations) > n): del temp_associations[n:] #trim to 300

        ret_dict[word] = [pair[0] for pair in temp_associations]
        del temp_associations[:] # clear

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
import nltk
nltk.download('wordnet')
def are_words_connected(board_word, clue, exception=False):
    wnl = nltk.stem.WordNetLemmatizer()
    return wnl.lemmatize(board_word) == wnl.lemmatize(clue) \
        or wnl.lemmatize(board_word, 'v') == wnl.lemmatize(clue, 'v') \
            or wnl.lemmatize(board_word, 'r') == wnl.lemmatize(clue, 'r') \
                or wnl.lemmatize(board_word, 'a') == wnl.lemmatize(clue, 'a') \
                    or (not exception and board_word in clue and len(board_word) > 3 and (clue.index(board_word) > 3 or clue.startswith(board_word)))

import nltk
nltk.download('wordnet')
def are_words_connected(board_word, clue, exception=False):
    wnl = nltk.stem.WordNetLemmatizer()
    return wnl.lemmatize(board_word) == wnl.lemmatize(clue) \
        or wnl.lemmatize(board_word, 'v') == wnl.lemmatize(clue, 'v') \
            or wnl.lemmatize(board_word, 'r') == wnl.lemmatize(clue, 'r') \
                or wnl.lemmatize(board_word, 'a') == wnl.lemmatize(clue, 'a') \
                    or (not exception and board_word in clue and len(board_word) > 3 and (clue.index(board_word) > 3 or clue.startswith(board_word)))

### MAIN
if __name__ == "__main__":
    vectors = r"raw_data/d2v_lm.txt"
    words = r"raw_data/common_boardwords.txt"
    output = r"data_objects/associator_objects/test_d2v_final_boardwords_associations.json" 

    generate(output, vectors, words, n=500, verbose=True)
    #txt_to_json(output, vectors)    