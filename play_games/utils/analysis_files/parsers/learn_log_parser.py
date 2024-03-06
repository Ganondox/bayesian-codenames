import copy

from play_games.utils.analysis_files.analysis_utils import LearnParseKeys, Stats


class LearnLogParser:
    def __init__(self):
        self.stat_dict = {}

    def get_values(self, f):
        line = f.readline()
        line = line.strip()
        values = line.split(": ")
        return values

    def parse_file(self, fp, counter):
        stat_dict = {}
        with open(fp, 'r') as f:
            learning_period_team_mate = ''
            for line in f:
                line = line.strip()
                values = line.split(": ")
                if values[0] == LearnParseKeys.START_TOKEN:
                    values = self.get_values(f)
                    learning_period_team_mate = values[1]
                    stat_dict[learning_period_team_mate] = {}
                elif values[0] == LearnParseKeys.CHOSEN_BOT_TOKEN:
                    if Stats.CHOSEN_BOTS_BY_ROUND not in stat_dict[learning_period_team_mate]:
                        stat_dict[learning_period_team_mate][Stats.CHOSEN_BOTS_BY_ROUND] = []
                    stat_dict[learning_period_team_mate][Stats.CHOSEN_BOTS_BY_ROUND].append(values[1])
                elif values[0] == LearnParseKeys.BOT_WEIGHTS_TOKEN:
                    values = self.get_values(f)
                    while values[0] != '':
                        #At this point, we know that we are in a learning period
                        if Stats.ARM_WEIGHTS_BY_ROUND not in stat_dict[learning_period_team_mate]:
                            stat_dict[learning_period_team_mate][Stats.ARM_WEIGHTS_BY_ROUND] = {}
                        #Create a list of the bot weights for each bot type in the ensamble for every round
                        if values[0] not in stat_dict[learning_period_team_mate][Stats.ARM_WEIGHTS_BY_ROUND]:
                            stat_dict[learning_period_team_mate][Stats.ARM_WEIGHTS_BY_ROUND][values[0]] = []
                        stat_dict[learning_period_team_mate][Stats.ARM_WEIGHTS_BY_ROUND][values[0]].append(float(values[1]))
                        values = self.get_values(f)
                elif values[0] == LearnParseKeys.END_TOKEN:
                    if Stats.GAME_WIN_LOSS not in stat_dict[learning_period_team_mate]:
                        stat_dict[learning_period_team_mate][Stats.GAME_WIN_LOSS] = []
                    if values[1] == 'win':
                        stat_dict[learning_period_team_mate][Stats.GAME_WIN_LOSS].append(1)
                    else:
                        stat_dict[learning_period_team_mate][Stats.GAME_WIN_LOSS].append(0)

        self.stat_dict[counter] = stat_dict

    def run_parser(self, file_paths):
        self.stat_dict.clear()
        counter = 0
        for file_path in file_paths:
            try:
                self.parse_file(file_path, counter)
                
            except:
                print("continue to next learn log")
            counter += 1
        return copy.deepcopy(self.stat_dict)