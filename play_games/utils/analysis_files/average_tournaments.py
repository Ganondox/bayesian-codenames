




import os, sys
import json
import numpy as np
import pandas as pd

def average(*files):
    columns_names = []
    rows_names = []

    average_wintimes = []
    average_winrate = []
    average_colt = []
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
                average_colt.append([])
                size.append([])
            for j, (g, stats) in enumerate( row.items()):

                if change: 
                    if g not in columns_names:
                        columns_names.append(g)
                    average_wintimes[i].append([])
                    average_winrate[i].append([])
                    average_colt[i].append([])
                    size[i].append(0)
                

                s = len(stats["Bot Pairing Scores"])
                average_wintimes[i][j].append(s*stats["Average Win Time"])
                average_winrate[i][j].append(s*stats["Win Rate"])
                average_colt[i][j].append(s*stats["Final Pair Score"])
                size[i][j]+=s
                
    print(size)
    print(rows_names)
    print(columns_names)
    
    size = np.array(size)
    return pd.DataFrame(np.sum(average_wintimes, axis=2)/size , index=rows_names, columns=columns_names), \
                pd.DataFrame(np.sum(average_winrate, axis=2)/size, index=rows_names, columns=columns_names), \
                pd.DataFrame(np.sum(average_colt, axis=2)/size, index=rows_names, columns=columns_names)
    


if __name__ == "__main__" :

    arguments = sys.argv[1:]

    if len(arguments) < 2:
        print("No arguments given")
        exit(-1)

    output_folder = arguments[0]

    input_files = arguments[1:]



    win_times, win_rates, colt_score = average(*input_files)
    os.makedirs(output_folder, exist_ok=True)

    win_times.to_csv(f"{output_folder}/win_times.csv")
    win_rates.to_csv(f"{output_folder}/win_rates.csv")
    colt_score.to_csv(f"{output_folder}/colt_scores.csv")
