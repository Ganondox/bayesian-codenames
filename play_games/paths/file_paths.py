import os

project_root = os.getcwd()
results_root = os.path.join(project_root, "stats")
assoc_root_path = os.path.join(project_root, "data_objects", "associator_objects")

config_file = os.path.join(project_root, "play_games", "configs", "config.ini")

###---Bot Component File Paths---###

w2v_boardwords_associations =         os.path.join(assoc_root_path, 'w2v_final_boardwords_associations.json')
glove_50_boardwords_associations =    os.path.join(assoc_root_path, 'glove_50_final_boardwords_associations.json')
glove_100_boardwords_associations =   os.path.join(assoc_root_path, 'glove_100_final_boardwords_associations.json')
glove_200_boardwords_associations =   os.path.join(assoc_root_path, 'glove_200_final_boardwords_associations.json')
glove_300_boardwords_associations =   os.path.join(assoc_root_path, 'glove_300_final_boardwords_associations.json')
w2v_glove_boardwords_associations =   os.path.join(assoc_root_path, 'w2v_glove_final_boardwords_associations.json')
cn_nb_boardwords_associations =       os.path.join(assoc_root_path, 'conceptnet-numberbatch_final_boardwords_associations.json')
d2v_boardwords_associations =         os.path.join(assoc_root_path, 'd2v_final_boardwords_associations.json')
elmo_boardwords_associations =        os.path.join(assoc_root_path, 'elmo_final_boardwords_associations.json')
bert1_boardwords_associations =       os.path.join(assoc_root_path, 'bert1_final_boardwords_associations.json')
bert2_boardwords_associations =       os.path.join(assoc_root_path, 'bert2_final_boardwords_associations.json')
fast_text_boardwords_associations =   os.path.join(assoc_root_path, 'fast-text_final_boardwords_associations.json')


w2v_vectors_path =          os.path.join(project_root, 'raw_data', 'w2v_lm.txt')
glove_50_vectors_path =     os.path.join(project_root, 'raw_data', 'glove_50_lm.txt')
glove_100_vectors_path =    os.path.join(project_root, 'raw_data', 'glove_100_lm.txt')
glove_200_vectors_path =    os.path.join(project_root, 'raw_data', 'glove_200_lm.txt')
glove_300_vectors_path =    os.path.join(project_root, 'raw_data', 'glove_300_lm.txt')
w2v_glove_vectors_path =    os.path.join(project_root, 'raw_data', 'w2v_glove_lm.txt')
cn_nb_vectors_path =        os.path.join(project_root, 'raw_data', 'conceptnet-numberbatch_lm.txt')
d2v_vectors_path =          os.path.join(project_root, 'raw_data','d2v_lm.txt')
elmo_vectors_path =         os.path.join(project_root, 'raw_data', 'elmo_lm.txt')
bert1_vectors_path =        os.path.join(project_root, 'raw_data', 'bert1_lm.txt')
bert2_vectors_path =        os.path.join(project_root, 'raw_data', 'bert2_lm.txt')
fast_text_vectors_path =    os.path.join(project_root, 'raw_data', 'fast-text_lm.txt')

###---filepaths to be set in file_manager---###
#all are implemented as arrays because the experiments use many of each
class ExperimentPaths:
    #raw data
    round_logs_dir_path = None
    learn_logs_dir_path = None
    round_log_filepaths = []
    learn_log_filepaths_cm = [] 
    learn_log_filepaths_g = []
    #data transformation
    parsed_data_dir_path = None
    processed_data_dir_path = None
    parsed_data_filepaths = []
    processed_data_filepaths = []

###---Word Pools---###
wordlist_path = os.path.join(project_root, 'raw_data', 'actual-final-wl.txt')
board_words_path = os.path.join(project_root, 'raw_data', 'common_boardwords.txt')
