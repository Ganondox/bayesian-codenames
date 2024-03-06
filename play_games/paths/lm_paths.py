from play_games.bots.types import LMType

from play_games.paths import file_paths


__LM_TO_VECTOR_PATH = {
    LMType.BERT1:         file_paths.bert1_vectors_path,
    LMType.BERT2:         file_paths.bert2_vectors_path,
    LMType.CN_NB:         file_paths.cn_nb_vectors_path,
    LMType.D2V:           file_paths.d2v_vectors_path,
    LMType.ELMO:          file_paths.elmo_vectors_path,
    LMType.FAST_TEXT:     file_paths.fast_text_vectors_path,
    LMType.GLOVE_50:      file_paths.glove_50_vectors_path,
    LMType.GLOVE_100:     file_paths.glove_100_vectors_path,
    LMType.GLOVE_200:     file_paths.glove_200_vectors_path,
    LMType.GLOVE_300:     file_paths.glove_300_vectors_path,
    LMType.W2V:           file_paths.w2v_vectors_path,
    LMType.W2V_GLOVE_50:   file_paths.w2v_glove_vectors_path,
    LMType.W2V_GLOVE_300:   [file_paths.w2v_vectors_path, file_paths.glove_300_vectors_path]
}

__LM_TO_ASSOCIATION_PATH = {
    LMType.BERT1:         file_paths.bert1_boardwords_associations,
    LMType.BERT2:         file_paths.bert2_boardwords_associations,
    LMType.CN_NB:         file_paths.cn_nb_boardwords_associations,
    LMType.D2V:           file_paths.d2v_boardwords_associations,
    LMType.ELMO:          file_paths.elmo_boardwords_associations,
    LMType.FAST_TEXT:     file_paths.fast_text_boardwords_associations,
    LMType.GLOVE_50:      file_paths.glove_50_boardwords_associations,
    LMType.GLOVE_100:     file_paths.glove_100_boardwords_associations,
    LMType.GLOVE_200:     file_paths.glove_200_boardwords_associations,
    LMType.GLOVE_300:     file_paths.glove_300_boardwords_associations,
    LMType.W2V:           file_paths.w2v_boardwords_associations,
    LMType.W2V_GLOVE_50:   file_paths.w2v_glove_boardwords_associations,
}

def get_vector_path_for_lm(lm: LMType) -> str:
    return __LM_TO_VECTOR_PATH.get(lm, None)

def get_association_path_for_lm(lm: LMType) -> str:
    return __LM_TO_ASSOCIATION_PATH.get(lm, None)