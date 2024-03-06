from os.path import join

from play_games.paths.creator.file_name_directory_elements import FileNameDirectoryElements as name_elements

def create_round_logs_files(experiment_paths, name_root, val):
    round_log_dir = experiment_paths.round_logs_dir_path
    parsed_data_dir = experiment_paths.parsed_data_dir_path
    processed_data_dir = experiment_paths.processed_data_dir_path
    tournament_table_dir = experiment_paths.tournament_tables_dir_path

    round_log_filename = f"{name_elements.ROUND_LOG_PREFIX}{name_root}_{val}{name_elements.ROUND_LOG_FILE_TYPE}"
    parsed_data_filename = f"{name_elements.PARSED_DATA_PREFIX}{name_root}_{val}{name_elements.PARSED_DATA_FILE_TYPE}"
    processed_data_filename = f"{name_elements.PROCESSED_DATA_PREFIX}{name_root}_{val}{name_elements.PROCESSED_DATA_PREFIX}"
    tournament_table_filename = f"{name_elements.TOURNAMENT_TABLE_PREFIX}{name_root}_{val}{name_elements.TOURNAMENT_TABLE_FILE_TYPE}"
    
    experiment_paths.round_log_filepaths.append(join(round_log_dir, round_log_filename))
    experiment_paths.parsed_data_filepaths.append(join(parsed_data_dir, parsed_data_filename))
    experiment_paths.processed_data_filepaths.append(join(processed_data_dir, processed_data_filename))
    experiment_paths.tournament_table_filepaths.append(join(tournament_table_dir, tournament_table_filename))