
'''
The purpose of this file is to simply parse and not to do any calculations.
This is part of the data gathering phase
'''

from play_games.utils.analysis_files.analysis_utils import RoundParseKeys, Stats
from play_games.bots.types import BotType


class RoundLogParser:
    def __init__(self):
        self.stat_dict = {}

    '''
    This is meant to be a helper function and shouldn't be called publicly

    This function parses a single file and puts the data into a stat dict. Save that dict to a parsed data file
    If you want to exclude bots from the file, too bad because that functionality should be in the data processing phase
    '''
    def parse_file(self, file_path, counter):
        stat_dict = {}
        with open(file_path, 'r') as f:
            curr_round = None
            curr_cm = None
            curr_g = None
            rwf = 0
            bwf = 0
            bywf = 0
            awf = 0
            while (line:= f.readline()):
                line = line.strip()
                values = line.split(": ")

                i = 0

                
                if values[0] == RoundParseKeys.CODEMASTER:
                    curr_cm = values[1]
                    if curr_cm not in stat_dict:
                        stat_dict[curr_cm] = {}

                if values[0] == RoundParseKeys.GUESSER:
                    curr_g = values[1]
                    if values[1] not in stat_dict[curr_cm]:
                        stat_dict[curr_cm][curr_g] = {}

                if values[0] == RoundParseKeys.N_TARGETS:
                    if Stats.CLUE_NUM_BY_ROUND not in stat_dict[curr_cm][curr_g]:
                        stat_dict[curr_cm][curr_g][Stats.CLUE_NUM_BY_ROUND] = []
                    stat_dict[curr_cm][curr_g][Stats.CLUE_NUM_BY_ROUND].append(int(values[1]))

                if values[0] == RoundParseKeys.CORRECT:
                    rwf += 1
                if values[0] == RoundParseKeys.BLUE:
                    bwf += 1
                if values[0] == RoundParseKeys.BYSTANDER:
                    bywf += 1
                if values[0] == RoundParseKeys.ASSASSIN:
                    awf += 1
                
                if values[0] == RoundParseKeys.ROUND:
                    curr_round = values[1]

                if (values[0] == RoundParseKeys.ROUND and values[1] != '1') or values[0] == RoundParseKeys.GAME_LOST \
                    or values[0] == RoundParseKeys.GAME_WON:
                
                    #Update the stats that are needed at the end of a round
                    if Stats.RED_WORDS_FLIPPED_BY_ROUND not in stat_dict[curr_cm][curr_g]:
                        stat_dict[curr_cm][curr_g][Stats.RED_WORDS_FLIPPED_BY_ROUND] = []
                    stat_dict[curr_cm][curr_g][Stats.RED_WORDS_FLIPPED_BY_ROUND].append(rwf)    
                    rwf = 0

                    if Stats.BLUE_WORDS_FLIPPED_BY_ROUND not in stat_dict[curr_cm][curr_g]:
                        stat_dict[curr_cm][curr_g][Stats.BLUE_WORDS_FLIPPED_BY_ROUND] = []
                    stat_dict[curr_cm][curr_g][Stats.BLUE_WORDS_FLIPPED_BY_ROUND].append(bwf)      
                    bwf = 0

                    if Stats.BYSTANDER_WORDS_FLIPPED_BY_ROUND not in stat_dict[curr_cm][curr_g]:
                        stat_dict[curr_cm][curr_g][Stats.BYSTANDER_WORDS_FLIPPED_BY_ROUND] = []
                    stat_dict[curr_cm][curr_g][Stats.BYSTANDER_WORDS_FLIPPED_BY_ROUND].append(bywf) 
                    bywf = 0

                    if Stats.ASSASSIN_WORDS_FLIPPED_BY_ROUND not in stat_dict[curr_cm][curr_g]:
                        stat_dict[curr_cm][curr_g][Stats.ASSASSIN_WORDS_FLIPPED_BY_ROUND] = []
                    stat_dict[curr_cm][curr_g][Stats.ASSASSIN_WORDS_FLIPPED_BY_ROUND].append(awf) 
                    awf = 0

                if values[0] == RoundParseKeys.GAME_WON or values[0] == RoundParseKeys.GAME_LOST:

                    #Update stats that are needed at the end of the game
                    if Stats.GAME_WIN_LOSS not in stat_dict[curr_cm][curr_g]:
                        stat_dict[curr_cm][curr_g][Stats.GAME_WIN_LOSS] = []
                    if Stats.NUM_ROUNDS_PER_GAME not in stat_dict[curr_cm][curr_g]:
                        stat_dict[curr_cm][curr_g][Stats.NUM_ROUNDS_PER_GAME] = []
                    stat_dict[curr_cm][curr_g][Stats.NUM_ROUNDS_PER_GAME].append(int(curr_round))

                if values[0] == RoundParseKeys.GAME_WON:
                    stat_dict[curr_cm][curr_g][Stats.GAME_WIN_LOSS].append(1)
                if values[0] == RoundParseKeys.GAME_LOST:
                    stat_dict[curr_cm][curr_g][Stats.GAME_WIN_LOSS].append(0)

        self.stat_dict[counter] = stat_dict
                    

    '''
    This is the function that should be called. 

    params: an array of file path(s) to parse
    output: a stat dictionary with all of the raw data needed for parsing
    '''
    def run_parser(self, file_paths):
        counter = 0
        for file_path in file_paths:
            try:
                self.parse_file(file_path, counter)
                
            except:
                print("missing file, move to next")
            counter += 1
        return self.stat_dict
