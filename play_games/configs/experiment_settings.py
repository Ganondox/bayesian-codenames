'''
This file has all of the overarching settings. Many of the files import this file and use these settings. 
It also is in charge of parsing the settings in the config file.

All objects that are shared among files are stored here. I store them here because a lot of the settings get changed at start up and need to 
be kept for all the files. 

'''

import json
import configparser

from play_games.configs.enums import ExperimentType, IndependentVariables, ConfigKeys
from play_games.bots.types import BotType

from play_games.paths import file_paths


class ExperimentSettings:

    config: configparser.ConfigParser
    config_setting: str

    ###---set these in config file---###
    tournament_setting: str
    custom_root_name: str | None

    #can be parameter experiment or learning experiment
    experiment_type: ExperimentType

    ###--Display-Parameters---###
    verbose_flag: bool
    print_boards: bool
    print_learning: bool

    ###---Experimental Settings---###

    #parameter experiment settings
    n_associations: int
    noise_parameters: list[float, float] | None
    detect: list[float, float] | None

    #don't touch this
    independent_variable: IndependentVariables | None
    variable_space: list[float | int] | None

    #Learning experiment settings
    iteration_range: list[int, int] | None
    include_same_lm: bool
    ensemble_parameters: float | None

    n_games: int
    board_size: int
    seed = float | int | str 
    spymasters: list[BotType]
    guessers: list[BotType]

    def __init__(self):
        ###---set this here---###
        self.config_setting: str = "DIST_ENS_W"
        #self.setup()

    def get_settings_from_config(self):
        self.config = configparser.ConfigParser()
        self.config.read(file_paths.config_file)

        config_section = self.config[self.config_setting]
        
        self.tournament_setting = read_string(config_section, ConfigKeys.TOURNAMENT_SETTING)
        self.custom_root_name = read_string(config_section, ConfigKeys.CUSTOM_ROOT_NAME, accept_null=True)

        self.experiment_type = read_enum(ExperimentType, config_section, ConfigKeys.EXPERIMENT_TYPE, accept_null=True, fallback=ExperimentType.TOURNAMENT)
        
        self.verbose_flag = read_boolean(config_section, ConfigKeys.VERBOSE_FLAG, fallback=False)
        self.print_boards = read_boolean(config_section, ConfigKeys.PRINT_BOARDS, fallback=False)
        self.print_learning = read_boolean(config_section, ConfigKeys.PRINT_LEARNING, fallback=False)

        self.n_associations = read_int(config_section, ConfigKeys.N_ASSOCIATIONS, fallback=300)
        self.noise_parameters = read_list(float, config_section, ConfigKeys.NOISE_PARAMETERS, fallback=None)
        self.detect = read_list(float, config_section, ConfigKeys.DETECT, fallback=None)

        self.independent_variable = read_enum(IndependentVariables, config_section, ConfigKeys.INDEPENDENT_VARIABLE, fallback=None)
        self.variable_space = read_json(config_section, ConfigKeys.VARIABLE_SPACE, fallback=None)

        self.iteration_range = read_list(int, config_section, ConfigKeys.ITERATION_RANGE, accept_null=True, fallback=None)
        self.include_same_lm = read_boolean(config_section, ConfigKeys.INCLUDE_SAME_LM, fallback=True)
        self.ensemble_parameters = read_float(config_section, ConfigKeys.ENSEMBLE_PARAMETERS, fallback=0.5)
        
        self.n_games = read_int(config_section, ConfigKeys.N_GAMES)
        self.board_size = read_int(config_section, ConfigKeys.BOARD_SIZE, fallback=25)

        bot_section = self.config[self.tournament_setting]

        self.spymasters = read_list(BotType, bot_section, ConfigKeys.SPYMASTERS)
        self.guessers = read_list(BotType, bot_section, ConfigKeys.GUESSERS)
        
    #This function gets the settings from config file, sets them, and makes assumptions from settings
    def setup(self):
        self.get_settings_from_config()
        if self.experiment_type is None: self.experiment_type = ExperimentType.TOURNAMENT
        if self.experiment_type == ExperimentType.PARAMETER_EXPERIMENT: 
            self.determine_variables()

    def determine_variables(self):
        #Here, we go through all the possible independent variables for an experiment and we find which one it is
        match(self.independent_variable):
            case IndependentVariables.N_ASSOCIATIONS:
                self.n_associations = self.variable_space
            case IndependentVariables.ENSEMBLE_PARAMETERS:
                self.ensemble_parameters = self.variable_space
            case IndependentVariables.NOISE_PARAMETERS:
                self.noise_parameters = self.variable_space


#_______________________________ CONFIG PARSING FUNCTIONS _______________________________#

def __check_fallback(section: configparser.SectionProxy, key, **kwargs):
    if not("fallback" in kwargs or key in section):
        print(f"{section.name}->{key} is required, but not found")
        exit(-1)

def __is_none(section: configparser.SectionProxy, key, accept_null):
    return accept_null is True and section.get(key).strip().lower() in ("null", "none", "")

def read_boolean(section: configparser.SectionProxy, key, **kwargs)->bool:
    __check_fallback(section, key, **kwargs)    

    try: 
        return section.getboolean(key, **kwargs)
    except ValueError:
        print(f"incorrect value for {section.name}->{key}. Set value as either 'True' or 'False'")
        exit(-1)


def read_int(section: configparser.SectionProxy, key, **kwargs)->int:
    __check_fallback(section, key, **kwargs)    

    try: 
        return section.getint(key, **kwargs)
    except ValueError:
        print(f"incorrect value for {section.name}->{key}. Set value as an integer")
        exit(-1)

def read_float(section: configparser.SectionProxy, key, **kwargs)->float:
    __check_fallback(section, key, **kwargs)    
    
    try: 
        return section.getfloat( key, **kwargs)
    except ValueError:
        print(f"incorrect value for {section.name}->{key}. Set value as an float")
        exit(-1)

def __read_raw(section: configparser.SectionProxy, key, accept_null, **kwargs):
    """Read the config section and return the string value if it passes checks and whether it passed those checks"""
    __check_fallback(section, key, **kwargs)
    if key not in section: return kwargs["fallback"], False
    if __is_none(section, key, accept_null): return None, False

    return section.get(key), True

def read_string(section, key, accept_null=False, **kwargs):
    text, _ = __read_raw(section, key, accept_null, **kwargs)
    return text

def read_enum(enum, section, key, accept_null=False, **kwargs):
    text, valid = __read_raw(section, key, accept_null, **kwargs)
    if not valid: return text

    try: 
        return enum(text)
    except ValueError:
        print(f"incorrect value for {section.name}->{key}. Set value as one of {[e.value for e in enum]}")
        exit(-1)

def read_json(section, key, accept_null=False, **kwargs):
    text, valid = __read_raw(section, key, accept_null, **kwargs)
    if not valid: return text

    try: 
        return json.loads(text)
    except json.JSONDecodeError:
        print(f"couldn't read {section.name}->{key} as valid JSON")
        exit(-1)

def read_list(cls, section, key, accept_null=False, **kwargs):
    text, valid = __read_raw(section, key, accept_null, **kwargs)
    if not valid: return text

    ls = read_json(section, key, **kwargs)

    if type(ls) is not list: 
        print(f"incorrect value for {section.name}->{key}. Set value as list of type {cls}")
        exit(-1)

    try: 
        return [cls(el) for el in ls]
    except ValueError:
        print(f"incorrect value for {section.name}->{key}. Set value as list of type {cls}")
        exit(-1)