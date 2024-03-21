from copy import deepcopy
from enum import IntEnum
from play_games.bots.guessers.noisy_guesser import NoisyGuesser
from play_games.bots.spymasters.bayesian_spymaster import BayesianSpymaster
from play_games.bots.spymasters.distance_associator_ai_spymaster import DistanceAssociatorAISpymaster
from play_games.bots.guessers.vector_baseline_guesser import VectorBaselineGuesser


class BotConstructorType(IntEnum):

    VECTOR_BASELINE_SPYMASTER =               1, None
    DISTANCE_ASSOCIATOR_AI_SPYMASTER =        3, DistanceAssociatorAISpymaster
    BAYESIAN_SPYMASTER =                      4, BayesianSpymaster
    VECTOR_BASELINE_GUESSER =                 7, VectorBaselineGuesser
    NOISY_GUESSER =                           8, NoisyGuesser
    
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
