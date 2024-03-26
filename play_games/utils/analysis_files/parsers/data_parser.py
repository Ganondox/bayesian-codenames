from play_games.paths import file_paths
from play_games.utils.analysis_files.analysis_utils import StatDictKeys, Types, save_json, load_json
from play_games.utils.analysis_files.parsers.learn_log_parser import LearnLogParser
from play_games.utils.analysis_files.parsers.round_log_parser import RoundLogParser
from play_games.bots.types import  AIType
from play_games.bots.types.bot_to_ai import get_ai


class DataParser:
    def __init__(self, experiment_paths):
        self.experiment_paths = experiment_paths
        self.round_log_parser = RoundLogParser()
        self.learn_log_parser = LearnLogParser()


    def parse_data(self, round_logs, learn_logs_cm, learn_logs_g, parsed_data_filepaths):

        #Compile the needed filepaths to parse

        #All experiments parse the round logs
        parsed_round_log_data = self.round_log_parser.run_parser(round_logs)

        #If it is a learning experiment, then we need to parse the learn logs as well
        if len(learn_logs_cm) != 0:
            parsed_learn_log_data_cm = self.learn_log_parser.run_parser(learn_logs_cm)
        if len(learn_logs_g) != 0:
            parsed_learn_log_data_g = self.learn_log_parser.run_parser(learn_logs_g)

        #Save the data
        final_dict = {}
        for counter, filepath in enumerate(parsed_data_filepaths):
            try:
                merged_dict = parsed_round_log_data[counter]
                if len(learn_logs_cm) != 0:
                    llcm_dict = parsed_learn_log_data_cm[counter]
                    self.merge_data(merged_dict, llcm_dict, Types.CM)
                if len(learn_logs_g) != 0:
                    llg_dict = parsed_learn_log_data_g[counter]
                    self.merge_data(merged_dict, llg_dict, Types.G)

                final_dict[counter] = merged_dict

                save_json(merged_dict, filepath)

            except:
                continue

        return final_dict

    def merge_data(self, merged_dict, learning_dict, type):
        for cm in merged_dict:
            for g in merged_dict[cm]:
                if type == Types.CM and (AIType.BAYESIAN == get_ai(cm)):
                    merged_dict[cm][g][StatDictKeys.CM_LEARN_STATS] = learning_dict[g]
                elif type == Types.G and (AIType.BAYESIAN == get_ai(g)):
                    merged_dict[cm][g][StatDictKeys.G_LEARN_STATS] = learning_dict[cm]

    def load_parsed_data(self):
        parsed_data = {}
        counter = 0
        for filepath in self.experiment_paths.parsed_data_filepaths:
            try:
                parsed_data[counter] = load_json(filepath)
            except:
                counter += 1
                continue
            counter += 1
        return parsed_data