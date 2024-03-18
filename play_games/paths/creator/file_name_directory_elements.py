class FileNameDirectoryElements:
    #file type elements for naming (type of log and literal type of file)
    ROUND_LOG_PREFIX = 'round_log_'
    ROUND_LOG_FILE_TYPE = '.txt'
    TOURNAMENT_TABLE_PREFIX = 'tournament_table_'
    TOURNAMENT_TABLE_FILE_TYPE = '.txt'
    LEARN_TABLE_PREFIX = 'learn_table_'
    LEARN_TABLE_FILE_TYPE = '.txt'
    PARAMETER_COMPARISON_FIGURE_PREFIX = "param_comparison_figs_"
    PARAMETER_COMPARISON_FIGURE_FILE_TYPE = ".jpg"
    PERFORMANCE_PROGRESSION_PREFIX = "performance_progression_"
    PERFORMANCE_PROGRESSION_SLIDING_WINDOW_PREFIX = "performance_progression_sliding_window_"
    ARM_PERCENTAGE_PREFIX = "arm_percentage_"
    ARM_WEIGHTS_PREFIX = "arm_weights_"
    FINAL_STAT_DIST_PREFIX = "final_stat_distribution_"
    LEARNING_FIGURE_FILE_TYPE = ".jpg"
    CM_STATS_FIGURE_PREFIX = "cm_stats_"
    CM_STATS_FIGURE_FILE_TYPE = ".jpg"
    PARSED_DATA_PREFIX = "parsed_data_"
    PARSED_DATA_FILE_TYPE = ".json"
    PROCESSED_DATA_PREFIX = "processed_data_"
    PROCESSED_DATA_FILE_TYPE = ".json"
    LEARN_LOG_PREFIX = 'learn_log_'
    LEARN_LOG_FILE_TYPE = '.txt'
    LEARN_PERIOD_ANALYSIS_PREFIX = "learn_period_analysis_"
    LEARN_PERIOD_ANALYSIS_FILE_TYPE = ".docx"
    LEARN_EXPERIMENT_ANALYSIS_PREFIX = "learn_experiment_analysis_"
    LEARN_EXPERIMENT_ANALYSIS_FILE_TYPE = ".docx"
    PARAM_EXPERIMENT_ANALYSIS_PREFIX = "param_experiment_analysis_"
    PARAM_EXPERIMENT_ANALYSIS_FILE_TYPE = ".docx"
    SPYMASTER_PREFIX = "cm_"
    GUESSER_PREFIX = "g_"

    #Directory elements
    #top level
    LEARNING_EXPERIMENTS_DIR = "learning_experiments"
    PARAMETER_EXPERIMENTS_DIR = "parameter_experiments"
    TOURNAMENTS_DIR = "tournaments"
    #second level
    PARSED_DATA_DIR = "parsed_data"
    PROCESSED_DATA_DIR = "processed_data"
    RAW_DATA_DIR = "raw_data"
    VISUALIZATIONS_DIR = "visualizations"
    LEARN_EXPERIMENT_ANALYSES_DIR = "learn_experiment_analyses"
    LEARN_PERIOD_ANALYSES_DIR = "learn_period_analyses"
    PARAM_EXPERIMENT_ANALYSES_DIR = "param_experiment_analyses"
    #third level
    LEARN_LOGS_DIR = "learn_logs"
    ROUND_LOGS_DIR = "round_logs"
    FIGURES_DIR = "figures"
    TABLES_DIR = "tables"
    #fourth level
    CM_STATS_DIR = "cm_stats"
    LEARN_FIGS_DIR = "learn_figs"
    PERC_SELECTED_DIR = "percent_selected_figs"
    ARM_WEIGHTS_DIR = "arm_weights_figs"
    PERF_PROG_DIR = "performance_progression_figs"
    PERF_PROG_SLIDE_WIND_DIR = "performance_progression_sliding_window_figs"
    TOURNAMENT_TABLES_DIR = "tournament_tables"
    LEARN_TABLES_DIR = "learn_tables"
    PARAM_COMPARISON_FIGS_DIR = "param_comparison_figs"
    FINAL_STAT_DIST_DIR = "final_stat_distribution_figs"


    #parameter elements for file naming
    N_GAMES_PREFIX = '_games.'
    N_ASSOCIATIONS_PREFIX = "_num_associations."
    LEARN_PERIOD_ITERATIONS_PREFIX = "_iteration(s)."
    PARAM_RANGE_PREFIX = "_param(s)."
    B_SIZE_PREFIX = "_board-size."
    WITH_LM = "_W"
    WITHOUT_LM = "_WO"
    IND_VAR_VAL = "_indep_var_val."

