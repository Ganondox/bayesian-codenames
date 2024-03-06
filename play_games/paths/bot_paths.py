from play_games.bots.types import BotType, AIType
from play_games.bots.types.bot_to_ai import get_ai
from play_games.bots.types.bot_to_lm import get_lm
from .lm_paths import get_association_path_for_lm, get_vector_path_for_lm


def __get_codemaster_paths(lm):
    return (get_association_path_for_lm(lm), get_vector_path_for_lm(lm))

def __get_guesser_paths(lm):
    return get_vector_path_for_lm(lm)
    
def get_paths_for_bot(bot_type_key: BotType) -> tuple[str, str] | str:
    lm_type = get_lm(bot_type_key)
    match get_ai(bot_type_key):    
        case AIType.DISTANCE_ASSOCIATOR:
            return __get_codemaster_paths(lm_type)
        case AIType.BASELINE:
            return __get_guesser_paths(lm_type)
        case _:
            return None
