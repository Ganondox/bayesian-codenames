from play_games.bots.ai_components.associator_ai_components.associator_data_cache import AssociatorDataCache
from play_games.bots.ai_components.associator_ai_components.vector_data_cache import VectorDataCache
from play_games.bots.types import LMType


LANGUAGE_MODELS = [LMType.W2V, LMType.GLOVE_100, LMType.CN_NB, LMType.D2V]

class InternalGuesser:

    def __init__(self, vector_filpath, associations_filepath):
        self.vectors = VectorDataCache(vector_filpath)
        self.associations = AssociatorDataCache(associations_filepath)
        self.associations.load_cache(500)
        self.__hash = hash(vector_filpath) + 33* hash(associations_filepath)


    def __hash__(self) -> int:
        return self.__hash