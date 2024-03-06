import scipy.spatial.distance as dist
import numpy as np
from json import load, dump 

def generate(output_path, model_path, words_path, frequencies_path, n=300, verbose=False):
    vectors = load_lm(model_path)
    if verbose: print("Parsed Embeddings")
    words = load_words(words_path)
    if verbose: print("Loaded Words... Starting generation")
    frequencies = load_freqs(frequencies_path)

    associations = gen_association(vectors, words, frequencies, n=n, verbose=verbose)

    with open(output_path, "w") as f:
        dump(associations, f)




# txt files are actually faster to parse
def txt_to_json(output_path, model_path):
    '''To convert txt to json embeddings'''
    vectors = load_lm(model_path)
    with open(output, "w") as f:
        dump(vectors, f)

### HELPER FUNCTIONS ###
embeddings = dict[str, list[float]]

def load_freqs(file_name: str) -> list[str, int]:
    with open(file_name, "r") as f:
        freqs = load(f)
        return freqs

def load_lm(file_name: str) -> embeddings:
    with open(file_name, "r") as f:
        if(file_name [-3:] == "txt"):
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

def gen_association(dist_dict: embeddings, board_word: list[str], frequency_list: dict[str, int],n=300, verbose=False) -> dict[str, list[str]]:
    temp_associations = []

    ret_dict = dict()
    for i, word in enumerate(board_word, start=1):
        for key in dist_dict.keys():
            if(key == word): 
                continue
            """fill in detect distance"""
            frequency = frequency_list[key]
            frequency_factor = 1/frequency
            detect_distance = dist.cosine(dist_dict[word], dist_dict[key]) + 10000000*frequency_factor
            pair = (key, detect_distance)
            ind = bin_search(pair, temp_associations)

            temp_associations.insert(ind, pair)
            
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

### MAIN
if __name__ == "__main__":
    vectors = r"raw_data/w2v_lm.txt"
    words = r"raw_data/common_boardwords.txt"
    output = r"data_objects/redone_associator_objects/DETECT-w2v-test-final-associations.json" 
    frequencies = r"raw_data/word_freqs.json"

    generate(output, vectors, words, frequencies, verbose=True)
    #txt_to_json(output, vectors)    
