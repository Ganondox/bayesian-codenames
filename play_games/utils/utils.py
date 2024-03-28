import os

def cond_print(msg, VERBOSE_FLAG):
    if VERBOSE_FLAG is True or VERBOSE_FLAG == 1:
        print(msg)


def load_word_list(path):
    with open(path, "r") as in_file:
        return [line.strip().lower() for line in in_file]
    

def create_path(fp):
    os.makedirs(os.path.dirname(fp), exist_ok=True)