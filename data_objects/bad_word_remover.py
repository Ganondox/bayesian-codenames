import json
import os, sys
import associations_creator as create


with open("raw_data/badwords.txt", "r") as file:
    bad_words = tuple(map(str.strip, file.read().lower().split()))

def process_vectors(vectors: list[str], associations):

    vectors = sorted(vectors)
    associations = sorted(associations)

    for i, file in enumerate(vectors):
        print(f"{i+1}/{len(vectors)} : {file}                         ", end="\r")
        dic = {}
        if file.endswith(('txt', 'vec')):
            good_lines = []
            with open(file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.split(maxsplit=1)[0] in new_words:
                        k = line.split(maxsplit=1)
                        v = tuple(map(float, k[1].strip().split()))
                        k = k[0]
                        dic[k] = v
                        good_lines.append(line)
            with open(file, 'w') as f:
                f.write("\n".join(good_lines))
        elif file.endswith('json'):
            with open(file, 'r') as f:
                js = f.read()
                info = json.loads(js)
            for k in info:
                if k in new_words:
                    dic[k] = info[k]
            
            with open(file, 'w') as f:
                json.dump(dic, f, sort_keys=True)

        word_path = r"raw_data/common_boardwords.txt"
        

       
        create.generate(associations[i], file, word_path, n=500, verbose=True)

def purge_list():
    with open("raw_data/actual-final-wl.txt", 'r') as file:
        original_words = set(map(str.strip, file.read().lower().split()))
    original_words.difference_update(bad_words)

    return tuple(sorted(original_words))


if __name__ == "__main__":

    arguments = sys.argv[1:]
    #print(arguments)
    output = None
    vectors = []
    associations = []

    mode = None
    for arg in arguments:
        
        if arg == '--v' or arg == '--a':
            mode = arg
        elif mode == '--v':
            vectors.append(arg)
        elif mode == '--a':
            associations.append(arg)
        elif mode is None:
            output = arg
    print("\n".join(sorted(vectors)), "\n".join(sorted(associations)))
    new_words = purge_list()
    with open(output, mode='w') as file:
        file.write("\n".join(new_words))

    new_words = set(new_words)

    process_vectors(vectors, associations)
