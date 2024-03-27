import os, sys
import json
import numpy as np
import pandas as pd

def average(*files):
    columns_names = []
    rows_names = []

    average_wintimes = []
    average_winrate = []
    average_turns_by_game = []
    red_words_flipped_by_game = []
    blue_words_flipped_by_game = []
    byst_words_flipped_by_game = []
    assa_words_flipped_by_game = []
    size = []

    for i, file in enumerate(files, 1):
        print(f"{i}/{len(files)}", end="\r")
        with open(file, "r") as f:
            data = json.load(f)
        
        for i, (cm, row) in enumerate(data.items()):
            change=False
            if cm not in rows_names:
                rows_names.append(cm)
                change=True
                average_wintimes.append([])
                average_winrate.append([])
                average_turns_by_game.append([])
                red_words_flipped_by_game.append([])
                blue_words_flipped_by_game.append([])
                byst_words_flipped_by_game.append([])
                assa_words_flipped_by_game.append([])
                size.append([])
            for j, (g, stats) in enumerate( row.items()):

                if change: 
                    if g not in columns_names:
                        columns_names.append(g)
                    average_wintimes[i].append([])
                    average_winrate[i].append([])
                    average_turns_by_game[i].append([])
                    red_words_flipped_by_game[i].append([])
                    blue_words_flipped_by_game[i].append([])
                    byst_words_flipped_by_game[i].append([])
                    assa_words_flipped_by_game[i].append([])                
                    size[i].append(0)
                

                s = len(stats["Blue Words Flipped By Game"])
                average_wintimes[i][j].append(s*stats["Average Win Time"])
                average_winrate[i][j].append(s*stats["Win Rate"])
                average_turns_by_game[i][j].append(s*stats["Average Turns By Game"])
                red_words_flipped_by_game[i][j].extend(stats["Red Words Flipped By Game"])
                blue_words_flipped_by_game[i][j].extend(stats["Blue Words Flipped By Game"])
                byst_words_flipped_by_game[i][j].extend(stats["Bystander Words Flipped By Game"])
                assa_words_flipped_by_game[i][j].extend(stats["Assassin Words Flipped By Game"])
                size[i][j]+=s
                
    print(size)
    print(rows_names)
    print(columns_names)
    
    size = np.array(size)
    return (
        pd.DataFrame(np.sum(average_wintimes, axis=2)/size , index=rows_names, columns=columns_names),
        pd.DataFrame(np.sum(average_winrate, axis=2)/size, index=rows_names, columns=columns_names),
        pd.DataFrame(np.sum(average_turns_by_game, axis=2)/size, index=rows_names, columns=columns_names),
        pd.DataFrame(np.average(red_words_flipped_by_game, axis=2), index=rows_names, columns=columns_names),
        pd.DataFrame(np.average(blue_words_flipped_by_game, axis=2), index=rows_names, columns=columns_names),
        pd.DataFrame(np.average(byst_words_flipped_by_game, axis=2), index=rows_names, columns=columns_names),
        pd.DataFrame(np.average(assa_words_flipped_by_game, axis=2), index=rows_names, columns=columns_names),
    )

    


if __name__ == "__main__" :

    arguments = sys.argv[1:]

    if len(arguments) < 2:
        print("No arguments given")
        exit(-1)

    output_folder = arguments[0]

    input_files = arguments[1:]


    labels = ("win_times", "win_rates", "turns_per_game", "team_words_per_game", "opponent_words_per_game", "bystander_words_per_game", "assassin_words_per_game")
    tables = average(*input_files)
    os.makedirs(output_folder, exist_ok=True)

    for label, table in zip(labels, tables):
        table.to_csv(os.path.join(output_folder, f"{label}.csv"))
