

from enum import StrEnum


class LearningAlgorithms(StrEnum):
    T3 = "T3"
    T4 = "T4"
    
    def __contains__(self, key):
        try:
            LearningAlgorithms(key)
            return True
        except ValueError:
            return False
    
class EnsembleCodemasterBots():
    def __init__(self):
        self.set_ensemble_cm_bots()
    
    def set_ensemble_cm_bots(self):
        from bots.types import AIType, BotType
        self.ensemble_cm_bots = {
            AIType.DISTANCE_ENSEMBLE: [BotType.W2V_DISTANCE_ASSOCIATOR, BotType.GLOVE_50_DISTANCE_ASSOCIATOR, BotType.GLOVE_100_DISTANCE_ASSOCIATOR, \
                BotType.GLOVE_200_DISTANCE_ASSOCIATOR, BotType.GLOVE_300_DISTANCE_ASSOCIATOR, BotType.W2V_GLOVE_DISTANCE_ASSOCIATOR, BotType.CN_NB_DISTANCE_ASSOCIATOR],
            AIType.RANDOM_DISTANCE_ENSEMBLE: [BotType.W2V_DISTANCE_ASSOCIATOR, BotType.GLOVE_50_DISTANCE_ASSOCIATOR, BotType.GLOVE_100_DISTANCE_ASSOCIATOR, \
                BotType.GLOVE_200_DISTANCE_ASSOCIATOR, BotType.GLOVE_300_DISTANCE_ASSOCIATOR, BotType.W2V_GLOVE_DISTANCE_ASSOCIATOR, BotType.CN_NB_DISTANCE_ASSOCIATOR]
        }
    
    def get_ensemble_cm_bots(self, ai_type_key):
        return self.ensemble_cm_bots[ai_type_key]

class EnsembleGuesserBots():
    def __init__(self):
        self.set_ensemble_g_bots()
    
    def set_ensemble_g_bots(self):
        from bots.types import AIType, BotType
        self.ensemble_g_bots = {
            AIType.DISTANCE_ENSEMBLE: [BotType.W2V_BASELINE_GUESSER, BotType.GLOVE_50_BASELINE_GUESSER, BotType.GLOVE_100_BASELINE_GUESSER, \
                BotType.GLOVE_200_BASELINE_GUESSER, BotType.GLOVE_300_BASELINE_GUESSER, BotType.W2V_GLOVE_BASELINE_GUESSER, BotType.CN_NB_BASELINE_GUESSER],
            AIType.RANDOM_DISTANCE_ENSEMBLE: [BotType.W2V_BASELINE_GUESSER, BotType.GLOVE_50_BASELINE_GUESSER, BotType.GLOVE_100_BASELINE_GUESSER, \
                BotType.GLOVE_200_BASELINE_GUESSER, BotType.GLOVE_300_BASELINE_GUESSER, BotType.W2V_GLOVE_BASELINE_GUESSER, BotType.CN_NB_BASELINE_GUESSER]
        }
    
    def get_ensemble_g_bots(self, ai_type_key):
        return self.ensemble_g_bots[ai_type_key]
