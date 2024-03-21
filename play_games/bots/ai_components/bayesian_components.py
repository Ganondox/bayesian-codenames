from play_games.bots.ai_components.associator_ai_components.associator_data_cache import AssociatorDataCache
from play_games.bots.ai_components.associator_ai_components.vector_data_cache import VectorDataCache
from play_games.bots.types import LMType
from play_games.paths import bot_paths


LANGUAGE_MODELS = [LMType.W2V, LMType.GLOVE_100, LMType.CN_NB, LMType.D2V]

N_ASSOC = 500

class InternalGuesser:

    def __init__(self, lm):
        self.lm = lm
        vector_filepath = bot_paths.get_vector_path_for_lm(lm),
        associations_filepath = bot_paths.get_association_path_for_lm(lm)
        if isinstance(vector_filepath, (tuple, list)):
            self.vectors = VectorDataCache(*vector_filepath)
        else:
            self.vectors = VectorDataCache(vector_filepath)

        self.associations = AssociatorDataCache(associations_filepath,)
        self.associations.load_cache(N_ASSOC)
        self.__hash = hash(vector_filepath) + 33* hash(associations_filepath)


    def __hash__(self) -> int:
        return self.__hash
    
    def __str__(self):
        return self.lm.__str__()
    
    def __repr__(self):
        return self.lm.__str__()