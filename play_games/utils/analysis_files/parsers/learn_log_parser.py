import copy
import json

from play_games.utils.analysis_files.analysis_utils import LearnParseKeys, Stats


class LearnLogParser:
    def __init__(self):
        self.stat_dict = {}

    def get_values(self, f):
        line = f.readline()
        line = line.strip()
        values = line.split(": ", maxsplit=1)
        return values

    def parse_file(self, fp, counter):
        stat_dict = {}
        with open(fp, 'r') as f:
            spymaster = ''
            learning_period_team_mate = ''
            for line in f:
                line = line.strip()
                values = line.split(": ", maxsplit=1)
                if values[0] == LearnParseKeys.START_TOKEN:
                    values = self.get_values(f)
                    spymaster = values[1]
                    if spymaster not in stat_dict:
                        stat_dict[spymaster] = {}
                elif values[0] == "GUESSER":
                    learning_period_team_mate = values[1]
                    if learning_period_team_mate not in stat_dict[spymaster]:
                        stat_dict[spymaster][learning_period_team_mate] = {}

                elif values[0] == "updated posterior":
                    if Stats.POSTERIORS_BY_ROUND not in stat_dict[spymaster][learning_period_team_mate]:
                        stat_dict[spymaster][learning_period_team_mate][Stats.POSTERIORS_BY_ROUND] = []
                    stat_dict[spymaster][learning_period_team_mate][Stats.POSTERIORS_BY_ROUND].append(json.loads(values[1]))
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