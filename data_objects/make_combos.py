from copy import copy
import sys
import os

sys.path.insert(0, os.getcwd())

from play_games.utils.object_manager import ObjectManager

import data_objects.associations_creator as associations_creator

def iterate_pairs(ls):
    c_ls:list = copy(ls)
    for a in ls:
        c_ls.remove(a)
        for b in c_ls:
            yield a,b

def get_first(string: str):
    return string.split(maxsplit=1)[0]

def get_descr(string: str):
    split = string.split(maxsplit=2)
    if split[0] in get_descr.common:
        return split[0]+split[1]
    return split[0].replace('-', '_')
get_descr.common = {'glove',}

import json
def load_lm(file_name: str):
    with open(file_name, "r") as f:
        if(file_name [-3:] == "txt"):
            vectors = dict()
            for line in f:
                ls = line.split()
                assert len(ls) > 1, "Can't read embeddings file"
                vectors[ls[0]] = [float(n) for n in ls[1:]]
            return vectors
        else:
            return json.load(f)

def combine(type1, type2, vectors):
    new = {}
    for key in vectors[type1]:
        new[key] = vectors[type1][key] + vectors[type2][key]
    return new


class FileRunner():
    def __init__(self):
        self.object_manager = ObjectManager()
    
    def add_combos(self) -> list[str]:

        lm_paths = []
        assoc_paths = []
        set_ai_types =[]
        set_lm_types = []
        
        bot_paths = [] 
        bot_types = []
        lm_types = []


        original_spymasters = copy(self.object_manager.experiment_settings.spymasters)
        original_guessers = copy(self.object_manager.experiment_settings.guessers)

        spymaster = copy(original_spymasters)
        guessers = copy(original_guessers)

        vectors = {}
        lm_i = 20

        total = len(spymaster) * (len(spymaster) - 1) / 2

        for g1 in original_guessers:
            type_ = get_descr(g1)
            path = self.object_manager.bot_paths.get_paths_for_bot(g1)

            vectors[type_] = load_lm(path)

        os.makedirs("combo_assoc", exist_ok=True)
        os.makedirs("combo_lm", exist_ok=True)

        for i, (g1, g2) in enumerate(iterate_pairs(original_guessers), 1):
            print(f"{i} / {total}")

            if get_first(g1) == get_first(g2): continue
            
           
            type1 = get_descr(g1)
            type2 = get_descr(g2)

            new_type = f"{type1}_{type2}"

            vector = combine(type1, type2, vectors)

            with open(f"combo_lm/{new_type}_lm.json", "w") as f:
                json.dump(vector, f)
            lm_paths.append(f"baseline_{new_type}_source_path = os.path.join(project_root, 'raw_data', 'combo_lm', '{new_type}_lm.json')")
            assoc_paths.append(f"{new_type}_boardwords_source_path = os.path.join(assoc_root_path, 'combo_assoc', '{new_type}_final_boardwords_associations.json')")
            associations_creator.generate(f"combo_assoc/{new_type}_final_boardwords_associations.json", f"combo_lm/{new_type}_lm.json", self.object_manager.file_paths_obj.board_words_path)

            bot_types.append(f"{new_type.upper()}_DISTANCE_ASSOCIATOR = '{new_type} distance associator'")
            bot_types.append(f"{new_type.upper()}_BASELINE_GUESSER = '{new_type} baseline guesser'")
            
            spymaster.append(f"{new_type} distance associator")
            guessers.append(f"{new_type} baseline guesser")

            
            lm_types.append(f"{new_type.upper()} = {lm_i}")
            lm_i += 1

            set_ai_types.append(f"self.bot_types.{new_type.upper()}_BASELINE_GUESSER : self.ai_types.BASELINE")
            set_ai_types.append(f"self.bot_types.{new_type.upper()}_DISTANCE_ASSOCIATOR : self.ai_types.DISTANCE_ASSOCIATOR")

            set_lm_types.append(f"self.bot_types.{new_type.upper()}_BASELINE_GUESSER : self.lm_types.{new_type.upper()}")
            set_lm_types.append(f"self.bot_types.{new_type.upper()}_DISTANCE_ASSOCIATOR : self.lm_types.{new_type.upper()}")

            bot_paths.append(f"self.bot_types.{new_type.upper()}_BASELINE_GUESSER : self.file_paths_obj.baseline_{new_type}_source_path")
            bot_paths.append(f"self.bot_types.{new_type.upper()}_DISTANCE_ASSOCIATOR : [self.file_paths_obj.{new_type}_boardwords_source_path, self.file_paths_obj.baseline_{new_type}_source_path]")

        with open("combo.txt", "w") as file:
            
            file.write("Added everything, copy 'combo_assoc' to dataobject and 'combo_lm' to raw_data")
            file.write("\n")
            file.write("Copy the following to FilePathsObj:")
            file.write("\n")
            file.write("\n".join(lm_paths))
            file.write("\n")
            file.write("\n".join(assoc_paths))
            file.write("\n")
            file.write("\nCopy the following to utils.py BotTypes:")
            file.write("\n")
            file.write("\n".join(bot_types))
            file.write("\n")
            file.write("\nCopy the following to utils.py LMTypes:")
            file.write("\n")
            file.write("\n".join(lm_types))
            file.write("\n")
            file.write("\nCopy the following to bot_parameter_settings.py AITypes:")
            file.write("\n")
            file.write(",\n".join(set_ai_types))
            file.write("\n")
            file.write("\nCopy the following to bot_parameter_settings.py LMTypes:")
            file.write("\n")
            file.write(",\n".join(set_lm_types))
            file.write("\n")
            file.write("\nCopy the following to bot_parameter_settings.py BotPaths:")
            file.write("\n")
            file.write(",\n".join(bot_paths))
            file.write("\n")
            file.write("\nHere is what you should put in config.ini")
            file.write("\n")
            file.write(str(spymaster).replace("'", '"'))
            file.write("\n")
            file.write(str(guessers).replace("'", '"'))
            file.write("\n")




if __name__=="__main__":

    #get arguments
    argv = sys.argv

    file_runner = FileRunner()
    
    seed=2000
    file_runner.object_manager.experiment_settings.config_setting = "TEST"
    file_runner.object_manager.experiment_settings.setup()
    
    file_runner.add_combos()
    
