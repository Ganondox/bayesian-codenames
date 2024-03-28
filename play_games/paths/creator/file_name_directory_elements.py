class FileNameDirectoryElements:
    #file type elements for naming (type of log and literal type of file)
    ROUND_LOG_PREFIX = 'round_log_'
    ROUND_LOG_FILE_TYPE = '.txt'
    PARSED_DATA_PREFIX = "parsed_data_"
    PARSED_DATA_FILE_TYPE = ".json"
    PROCESSED_DATA_PREFIX = "processed_data_"
    PROCESSED_DATA_FILE_TYPE = ".json"
    LEARN_LOG_PREFIX = 'learn_log_'
    LEARN_LOG_FILE_TYPE = '.txt'

    #Directory elements
    #top level
    TOURNAMENTS_DIR = "tournaments"
    #second level
    PARSED_DATA_DIR = "parsed_data"
    PROCESSED_DATA_DIR = "processed_data"
    RAW_DATA_DIR = "raw_data"
    #third level
    LEARN_LOGS_DIR = "learn_logs"
    ROUND_LOGS_DIR = "round_logs"

    #parameter elements for file naming
    N_GAMES_PREFIX = '_games.'
    B_SIZE_PREFIX = "_board-size."

