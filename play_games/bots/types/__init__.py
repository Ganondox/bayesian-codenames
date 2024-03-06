# Access all the nessecary enums from here
from enum import StrEnum

class AIType(StrEnum):
    DISTANCE_ASSOCIATOR = "distance_associator"
    NOISY_DISTANCE_ASSOCIATOR = "noisy_distance_associator"
    NOISY_BASELINE = "noisy_baseline"
    BASELINE = "baseline"
    DISTANCE_ENSEMBLE = "distance ensemble"
    RANDOM_DISTANCE_ENSEMBLE = "random distance ensemble"

class BotType(StrEnum):
    W2V_GLOVE_BASELINE_GUESSER = 'w2v_glove baseline guesser'
    W2V_BASELINE_GUESSER = "w2v baseline guesser"
    GLOVE_50_BASELINE_GUESSER = "glove 50 baseline guesser"
    GLOVE_100_BASELINE_GUESSER = "glove 100 baseline guesser"
    GLOVE_200_BASELINE_GUESSER = "glove 200 baseline guesser"
    GLOVE_300_BASELINE_GUESSER = "glove 300 baseline guesser"
    CN_NB_BASELINE_GUESSER = "cn_nb baseline guesser"
    D2V_BASELINE_GUESSER = "d2v baseline guesser"
    ELMO_BASELINE_GUESSER = "elmo baseline guesser"
    BERT1_BASELINE_GUESSER = "bert1 baseline guesser"
    BERT2_BASELINE_GUESSER = "bert2 baseline guesser"
    FAST_TEXT_BASELINE_GUESSER = "fast-text baseline guesser"

    W2V_DISTANCE_ASSOCIATOR = "w2v distance associator"
    GLOVE_300_DISTANCE_ASSOCIATOR = "glove 300 distance associator"
    GLOVE_50_DISTANCE_ASSOCIATOR = "glove 50 distance associator"
    GLOVE_100_DISTANCE_ASSOCIATOR = "glove 100 distance associator"
    GLOVE_200_DISTANCE_ASSOCIATOR = "glove 200 distance associator"
    W2V_GLOVE_DISTANCE_ASSOCIATOR = "w2v_glove distance associator"
    CN_NB_DISTANCE_ASSOCIATOR = "cn_nb distance associator"
    D2V_DISTANCE_ASSOCIATOR = "d2v distance associator"
    ELMO_DISTANCE_ASSOCIATOR = "elmo distance associator"
    BERT1_DISTANCE_ASSOCIATOR = "bert1 distance associator"
    BERT2_DISTANCE_ASSOCIATOR = "bert2 distance associator"
    FAST_TEXT_DISTANCE_ASSOCIATOR = "fast-text distance associator"

    NOISY_DISTANCE_ASSOCIATOR = "noisy distance associator"
    NOISY_BASELINE_GUESSER = "noisy baseline guesser"

    DISTANCE_ENSEMBLE_CODEMASTER = "distance ensemble codemaster"
    DISTANCE_ENSEMBLE_GUESSER = "distance ensemble guesser"
    
    RANDOM_DISTANCE_ENSEMBLE_GUESSER = "random distance ensemble guesser"
    RANDOM_DISTANCE_ENSEMBLE_CODEMASTER= "random distance ensemble codemaster"

    @property
    def ai_type(self)->AIType:
        from play_games.bots.types.bot_to_ai import get_ai
        return get_ai(self)
    
    @property
    def lm_type(self)->'LMType':
        from play_games.bots.types.bot_to_lm import get_lm
        return get_lm(self)

class LMType(StrEnum):
    W2V = 'w2v'
    W2V_GLOVE_50 = "w2v_glove_50"
    GLOVE_50 = 'glove 50'
    GLOVE_100 = 'glove 100'
    GLOVE_200 = 'glove 200'
    GLOVE_300 = 'glove 300'
    CN_NB = 'cn_nb'
    W2V_GLOVE_300 = "w2v_glove_300"
    D2V = 'd2v'
    ELMO = 'elmo'
    BERT1 = 'bert1'
    BERT2 = 'bert2'
    FAST_TEXT = 'fast-text'
    NONE = '[NONE]'
    ENSEMBLE = 'ensemble'
    RANDOM_ENSEMBLE = 'random ensemble'
    NOISY = 'noisy'

