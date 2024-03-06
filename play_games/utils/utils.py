import os
import warnings
import joblib

from play_games.paths import file_paths


def cond_print(msg, VERBOSE_FLAG):
    if VERBOSE_FLAG is True or VERBOSE_FLAG == 1:
        print(msg)

def quick_dist(vec1, vec2):
    num = vec1.dot(vec2)
    sign = -1 if num < 0 else 1
    return 1- sign * num * num / (vec1.dot(vec1) * vec2.dot(vec2))


def load_word_list(path):
    with open(path, "r") as in_file:
        return [line.strip().lower() for line in in_file]
    

def create_path(fp):
    os.makedirs(os.path.dirname(fp), exist_ok=True)

__colt_model_cache = None
def load_colt_model():
    global __colt_model_cache
    if not __colt_model_cache:
        __colt_model_cache = load_joblib_no_warnings(file_paths.model_path)
    return __colt_model_cache

    
def load_joblib_no_warnings(filepath):
    with warnings.catch_warnings():
        # ignore all caught warnings
        warnings.filterwarnings("ignore")
        return joblib.load(filepath)