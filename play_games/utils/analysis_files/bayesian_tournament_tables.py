import os, sys
import json
import numpy as np
import pandas as pd

def average(*files):
    columns_names = []
    rows_names = []

    average_wintimes = {}
    average_winrate = {}
    average_turns_by_game = {}
    red_words_flipped_by_game = {}
    blue_words_flipped_by_game = {}
    byst_words_flipped_by_game = {}
    assa_words_flipped_by_game = {}
    size = {}

    for i, file in enumerate(files, 1):
        print(f"{i}/{len(files)}", end="\r")
        with open(file, "r") as f:
            data = json.load(f)
        
        for i, (cm, row) in enumerate(data.items()):
            change=False
            if cm not in rows_names:
                rows_names.append(cm)
                change=True
                average_wintimes[cm] = {}
                average_winrate[cm] = {}
                average_turns_by_game[cm] = {}
                red_words_flipped_by_game[cm] = {}
                blue_words_flipped_by_game[cm] = {}
                byst_words_flipped_by_game[cm] = {}
                assa_words_flipped_by_game[cm] = {}
                size[cm] = {}
            for j, (g, stats) in enumerate(row.items()):

                if change: 
                    if g not in columns_names:
                        columns_names.append(g)
                    average_wintimes[cm][g] = []
                    average_winrate[cm][g] = []
                    average_turns_by_game[cm][g] = []
                    red_words_flipped_by_game[cm][g] = []
                    blue_words_flipped_by_game[cm][g] = []
                    byst_words_flipped_by_game[cm][g] = []
                    assa_words_flipped_by_game[cm][g] = []                
                    size[cm][g] = 0
                

                s = len(stats["Blue Words Flipped By Game"])
                average_wintimes[cm][g].append(s*stats["Average Win Time"])
                average_winrate[cm][g].append(s*stats["Win Rate"])
                average_turns_by_game[cm][g].append(s*stats["Average Turns By Game"])
                red_words_flipped_by_game[cm][g].extend(stats["Red Words Flipped By Game"])
                blue_words_flipped_by_game[cm][g].extend(stats["Blue Words Flipped By Game"])
                byst_words_flipped_by_game[cm][g].extend(stats["Bystander Words Flipped By Game"])
                assa_words_flipped_by_game[cm][g].extend(stats["Assassin Words Flipped By Game"])
                size[cm][g]+=s
                
    # print(size)
    # print(rows_names)
    # print(columns_names)
    print(len(average_wintimes), [len(a) for a in average_wintimes])

    average_wintimes = [[ None if cm not in size or g not in size[cm] else np.average(average_wintimes[cm][g]) for g in columns_names] for cm in rows_names]
    average_winrate = [[ None if cm not in size or g not in size[cm] else np.average(average_winrate[cm][g]) for g in columns_names] for cm in rows_names]
    average_turns_by_game = [[ None if cm not in size or g not in size[cm] else np.average(average_turns_by_game[cm][g]) for g in columns_names] for cm in rows_names]
    red_words_flipped_by_game = [[ None if cm not in size or g not in size[cm] else np.average(red_words_flipped_by_game[cm][g]) for g in columns_names] for cm in rows_names]
    blue_words_flipped_by_game = [[ None if cm not in size or g not in size[cm] else np.average(blue_words_flipped_by_game[cm][g]) for g in columns_names] for cm in rows_names]
    byst_words_flipped_by_game = [[ None if cm not in size or g not in size[cm] else np.average(byst_words_flipped_by_game[cm][g]) for g in columns_names] for cm in rows_names]
    assa_words_flipped_by_game = [[ None if cm not in size or g not in size[cm] else np.average(assa_words_flipped_by_game[cm][g]) for g in columns_names] for cm in rows_names]

    # average_wintimes = [[ sum(inner)/size[i][j]  for j, inner in enumerate(outer)] for i, outer in enumerate(average_wintimes)]
    # average_winrate = [[ sum(inner)/size[i][j]  for j, inner in enumerate(outer)] for i, outer in enumerate(average_winrate)]
    # average_turns_by_game = [[ sum(inner)/size[i][j]  for j, inner in enumerate(outer)] for i, outer in enumerate(average_turns_by_game)]
    # red_words_flipped_by_game = [[ np.average(inner)  for j, inner in enumerate(outer)] for i, outer in enumerate(red_words_flipped_by_game)]
    # blue_words_flipped_by_game = [[np.average(inner)  for j, inner in enumerate(outer)] for i, outer in enumerate(blue_words_flipped_by_game)]
    # byst_words_flipped_by_game = [[ np.average(inner)  for j, inner in enumerate(outer)] for i, outer in enumerate(byst_words_flipped_by_game)]
    # assa_words_flipped_by_game = [[ np.average(inner)  for j, inner in enumerate(outer)] for i, outer in enumerate(assa_words_flipped_by_game)]
    
    return (
        pd.DataFrame(average_wintimes, index=rows_names, columns=columns_names),
        pd.DataFrame(average_winrate, index=rows_names, columns=columns_names),
        pd.DataFrame(average_turns_by_game, index=rows_names, columns=columns_names),
        pd.DataFrame(red_words_flipped_by_game, index=rows_names, columns=columns_names),
        pd.DataFrame(blue_words_flipped_by_game, index=rows_names, columns=columns_names),
        pd.DataFrame(byst_words_flipped_by_game, index=rows_names, columns=columns_names),
        pd.DataFrame(assa_words_flipped_by_game, index=rows_names, columns=columns_names),
    )

    


if __name__ == "__main__" :

    arguments = sys.argv[1:]

    # if len(arguments) < 2:
    #     print("No arguments given")
    #     exit(-1)

    output_folder = arguments[0]
    # output_folder = "outt"
    input_files = arguments[1:]
    # input_files = [os.path.join(r"C:\Users\Researcher\Downloads\PROCESSED\stats\saved_results\100_bayesian\processed_data", a) for a in os.listdir(r"C:\Users\Researcher\Downloads\PROCESSED\stats\saved_results\100_bayesian\processed_data")]


    labels = ("win_times", "win_rates", "turns_per_game", "team_words_per_game", "opponent_words_per_game", "bystander_words_per_game", "assassin_words_per_game")
    tables = average(*input_files)
    os.makedirs(output_folder, exist_ok=True)

    for label, table in zip(labels, tables):
        table.to_csv(os.path.join(output_folder, f"{label}.csv"))
