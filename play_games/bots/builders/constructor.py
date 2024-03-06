from copy import deepcopy
from enum import IntEnum
from play_games.bots.codemasters.distance_associator_ai_codemaster import DistanceAssociatorAICodemaster
from play_games.bots.codemasters.ensemble_ai_codemaster import EnsembleAICodemaster
from play_games.bots.codemasters.noisy_distance_associator_codemaster import NoisyDistanceAssociatorAICodemaster
from play_games.bots.guessers.ensemble_ai_guesser import EnsembleAIGuesser
from play_games.bots.guessers.noisy_ai_guesser import NoisyAIGuesser
from play_games.bots.guessers.vector_baseline_guesser import VectorBaselineGuesser


class BotConstructorType(IntEnum):

    VECTOR_BASELINE_CODEMASTER =               1, None
    ENSEMBLE_AI_CODEMASTER =                   2, EnsembleAICodemaster
    DISTANCE_ASSOCIATOR_AI_CODEMASTER =        3, DistanceAssociatorAICodemaster
    NOISY_DISTANCE_ASSOCIATOR_AI_CODEMASTER =  4, NoisyDistanceAssociatorAICodemaster
    NOISY_VECTOR_BASELINE_GUESSER =            5, NoisyAIGuesser
    VECTOR_BASELINE_GUESSER =                  7, VectorBaselineGuesser
    ENSEMBLE_AI_GUESSER =                      8, EnsembleAIGuesser
    RANDOM_ENSEMBLE_AI_CODEMASTER =            10, EnsembleAICodemaster
    RANDOM_ENSEMBLE_AI_GUESSER =               11, EnsembleAIGuesser
    
    def __new__(cls, value, contr, *args, **kwargs):
        obj = int.__new__(cls)
        obj._value_ = value
        obj.constructor = contr
        return obj
    
    # def __init__(self, val, cls):
    #     pass

    def build(self, *args, **kwargs):
        if isinstance(self.constructor, type):
            return self.constructor(*args, **kwargs)
        else:
            return deepcopy(self.constructor)
