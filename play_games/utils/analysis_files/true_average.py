




import os, sys
import json
import numpy as np
import pandas as pd
import scipy.stats as pystats


def summary(arr):
    mean = np.mean(arr) 
    n = len(arr)
    std_error = pystats.sem(arr)
    #we use the t distribution to account for non-normal distributions
    t = pystats.t.ppf((1 + .95) / 2, n-1)
    margin_of_error = t * std_error 

    return mean, margin_of_error

def min(arr):
    a=[]
    for i in range(len(arr[0])):
        b=sorted(arr[:,i])
        for e in b:
            if e!=0:
                a.append(e)
                break
        else:
            a.append(0)

    return a

def running(arr: np.ndarray, limit=None):
    ans = np.zeros(arr.shape)

    
    ans[0] = arr[0]
    for i in range(1, len(arr)):
        ans[i] = ans[i-1] + arr[i]
    
    ans = ans/np.arange(1, 51)[:, np.newaxis]

    return ans

def sliding(arr, limit=None):
    ans = np.zeros(arr.shape)

    ans[-1] = arr[-1]
    for i in range(len(arr)-1, -1, -1):
        ans[i] = ans[i+1] + arr[i]
    
    ans = ans/np.arange(50, 0, -1)[:, np.newaxis]
    
    return ans

def running_wt(arr, limit):
    ans = np.zeros(arr.shape)

    sum = np.zeros(arr.shape[1])
    count = np.zeros(arr.shape[1])
    for i in range( len(arr)):

        for j in range(len(arr[i])):
            if limit[i][j] == 1:
               sum[j] += arr[i][j]
               count[j]+= 1

            if count[j] == 0:
                ans[i][j] = 0
            else:
                ans[i][j] =sum[j]/count[j]    

    return ans

def sliding_wt(arr, limit):
    ans = np.zeros(arr.shape)
    sum = np.sum(arr, where=(limit==1), axis=0)
    count = np.count_nonzero.zeros(arr.shape[1])
    for i in range( len(arr)):
        for j in range(len(arr[i])):
           
            if count[j] == 0:
                ans[i][j] = arr[i-1][j] if i != 0 else 0
            else:
                ans[i][j] =sum[j]/count[j]

            if limit[i][j] == 1:
                sum[j] -= arr[i-1][j]
                count[j]-= 1
    return ans

def average(*files):
    stats = {}

    codemasters={"w2v distance associator", "cn_nb distance associator", "elmo distance associator", "bert distance associator", "glove 100 distance associator", "glove 200 distance associator", "glove 300 distance associator", "w2v_glove50 distance associator"}
    guessers={"w2v baseline guesser", "cn_nb baseline guesser", "elmo baseline guesser", "bert baseline guesser", "glove 100 baseline guesser", "glove 200 baseline guesser", "glove 300 baseline guesser", "w2v_glove300 baseline guesser"}



    for i, file in enumerate(files, 1):
        print(f"{i}/{len(files)}", end="\r")
        with open(file, "r") as f:
            data = json.load(f)
        
        for i, (cm, row) in enumerate(data.items()):
            if cm not in codemasters: continue

            if cm not in stats:
                stats[cm] = {}

            cm_stats = stats[cm]

            for j, (g, imp_stats) in enumerate( row.items()):
                if g not in guessers: continue
             
                if g not in cm_stats:
                    cm_stats[g] = {
                        'all_winrate': [],
                        'all_wintime': [],
                        'all_coltscore': [],
                        'all_redflipped': [],
                        'all_blueflipped': [],
                        'all_bystflipped': [],
                        'all_assaflipped': [],
                        'game_count': 0,
                        'per_game_winrate': [[] for _ in range(50)],
                        'per_game_wintime': [[] for _ in range(50)],
                        'per_game_coltscore': [[] for _ in range(50)],
                        'per_game_redflipped': [[] for _ in range(50)],
                        'per_game_blueflipped': [[] for _ in range(50)],
                        'per_game_bystflipped': [[] for _ in range(50)],
                        'per_game_assaflipped': [[] for _ in range(50)],
                    }

                pair_stats = cm_stats[g]                                   
                
                win_rate_sum = 0
                win_time_sum = 0
                count = 1
                wt_count=0

                big_zip = zip(imp_stats["Running Average Win Rate"], imp_stats["Running Average Win Time"], imp_stats["Bot Pairing Scores"], imp_stats["Red Words Flipped By Game"], imp_stats["Blue Words Flipped By Game"], imp_stats["Bystander Words Flipped By Game"], imp_stats["Assassin Words Flipped By Game"])
                for run_winrate, run_wintime, colt, red, blue, byst, assa in big_zip:
                    game_id = pair_stats['game_count'] % 50
                    winrate = run_winrate*count - win_rate_sum
                    
                    win_rate_sum+=winrate
                    
                    if winrate > 0.00001: 
                        wt_count+=1
                        wintime = run_wintime*wt_count - win_time_sum
                        win_time_sum+=wintime
                        pair_stats['all_wintime'].append(wintime)
                        pair_stats['per_game_wintime'][game_id].append(wintime)
                    else:
                        pair_stats['per_game_wintime'][game_id].append(pair_stats['all_wintime'][-1] if pair_stats['all_wintime'] else 0)

                    pair_stats['all_winrate'].append(winrate)
                    pair_stats['per_game_winrate'][game_id].append(winrate)
                    pair_stats['all_coltscore'].append(colt)
                    pair_stats['per_game_coltscore'][game_id].append(colt)
                    pair_stats['all_redflipped'].append(red)
                    pair_stats['per_game_redflipped'][game_id].append(red)
                    pair_stats['all_blueflipped'].append(blue)
                    pair_stats['per_game_blueflipped'][game_id].append(blue)
                    pair_stats['all_bystflipped'].append(byst)
                    pair_stats['per_game_bystflipped'][game_id].append(byst)
                    pair_stats['all_assaflipped'].append(assa)
                    pair_stats['per_game_assaflipped'][game_id].append(assa)
                    pair_stats['game_count']+=1
                    
                    count+=1
    result = {}

    
    for cm in stats:
        result[cm] = {}
        for g in stats[cm]:
            result[cm][g]={}
            local = result[cm][g]

            stats[cm][g]['all_winrate'] = np.array(stats[cm][g]['all_winrate'])
            stats[cm][g]['all_wintime'] = np.array(stats[cm][g]['all_wintime'])
            stats[cm][g]['per_game_wintime'] = np.array(stats[cm][g]['per_game_wintime'])
            stats[cm][g]['per_game_winrate'] = np.array(stats[cm][g]['per_game_winrate'])
            stats[cm][g]['all_coltscore'] = np.array(stats[cm][g]['all_coltscore'])
            stats[cm][g]['per_game_coltscore'] = np.array(stats[cm][g]['per_game_coltscore'])
            stats[cm][g]['all_redflipped'] = np.array(stats[cm][g]['all_redflipped'])
            stats[cm][g]['per_game_redflipped'] = np.array(stats[cm][g]['per_game_redflipped'])
            stats[cm][g]['all_blueflipped'] = np.array(stats[cm][g]['all_blueflipped'])
            stats[cm][g]['per_game_blueflipped'] = np.array(stats[cm][g]['per_game_blueflipped'])
            stats[cm][g]['all_bystflipped'] = np.array(stats[cm][g]['all_bystflipped'])
            stats[cm][g]['per_game_bystflipped'] = np.array(stats[cm][g]['per_game_bystflipped'])
            stats[cm][g]['all_assaflipped'] = np.array(stats[cm][g]['all_assaflipped'])
            stats[cm][g]['per_game_assaflipped'] = np.array(stats[cm][g]['per_game_assaflipped'])


            local["Win Rate"] = summary(stats[cm][g]['all_winrate'])
            local["Average Win Time"] = summary(stats[cm][g]['all_wintime'])
            local["Final Pair Score"] = summary(stats[cm][g]['all_coltscore'])
            local["Average Red Words Flipped By Game"] = summary(stats[cm][g]['all_redflipped'])
            local["Average Blue Words Flipped By Game"] = summary(stats[cm][g]['all_blueflipped'])
            local["Average Bystander Words Flipped By Game"] = summary(stats[cm][g]['all_bystflipped'])
            local["Average Assassin Words Flipped By Game"] = summary(stats[cm][g]['all_assaflipped']) 
            local["Min Win Time"] = summary(min(stats[cm][g]['per_game_wintime']))     

            local["Bot Pairing Scores"] = np.average(stats[cm][g]['per_game_coltscore'], axis=1).tolist()
            local["Red Words Flipped By Game"] = np.average(stats[cm][g]['per_game_redflipped'], axis=1).tolist()
            local["Blue Words Flipped By Game"] = np.average(stats[cm][g]['per_game_blueflipped'], axis=1).tolist()
            local["Bystander Words Flipped By Game"] = np.average(stats[cm][g]['per_game_bystflipped'], axis=1).tolist()
            local["Assassin Words Flipped By Game"] = np.average(stats[cm][g]['per_game_assaflipped'], axis=1).tolist()    

            local["Running Average Win Rate"] = np.average(running(stats[cm][g]['per_game_winrate']),axis=1).tolist()
            local["Running Average Win Time"] = np.average(running_wt(stats[cm][g]['per_game_wintime'], stats[cm][g]['per_game_winrate']),axis=1).tolist()
            local["Running Average Red Words Flipped By Game"] = np.average(running(stats[cm][g]['per_game_redflipped']),axis=1).tolist()
            local["Running Average Blue Words Flipped By Game"] = np.average(running(stats[cm][g]['per_game_blueflipped']),axis=1).tolist()
            local["Running Average Bystander Words Flipped By Game"] = np.average(running(stats[cm][g]['per_game_bystflipped']),axis=1).tolist()
            local["Running Average Assassin Words Flipped By Game"] = np.average(running(stats[cm][g]['per_game_assaflipped']),axis=1).tolist()

            local["Sliding Window Average Win Rate"] = np.average(running(stats[cm][g]['per_game_winrate']),axis=1).tolist()
            local["Sliding Window Average Win Time"] = np.average(running_wt(stats[cm][g]['per_game_wintime'], stats[cm][g]['per_game_winrate']),axis=1).tolist()
            local["Sliding Window Average Pair Score"] = np.average(running(stats[cm][g]['per_game_coltscore']),axis=1).tolist()
            local["Sliding Window Average Red Words Flipped By Game"] = np.average(running(stats[cm][g]['per_game_redflipped']),axis=1).tolist()
            local["Sliding Window Average Blue Words Flipped By Game"] = np.average(running(stats[cm][g]['per_game_blueflipped']),axis=1).tolist()
            local["Sliding Window Average Bystander Words Flipped By Game"] = np.average(running(stats[cm][g]['per_game_bystflipped']),axis=1).tolist()
            local["Sliding Window Average Assassin Words Flipped By Game"] = np.average(running(stats[cm][g]['per_game_assaflipped']),axis=1).tolist()
    
    with open("Output_trial.json", 'w') as f:
        json.dump(result, f)


if __name__ == "__main__" :

    arguments = sys.argv[1:]
    print(arguments)
    if len(arguments) < 2:
        print("No arguments given")
    
        input_files= r"D:\codenames\COMBO_RESULTS\compute\codenames-ai\stats\saved_results\tournaments\processed_data\\"
        input_files = [r"D:\codenames\COMBO_RESULTS\compute\codenames-ai\stats\saved_results\tournaments\processed_data\\"+v for v in os.listdir(input_files)]
    else:
        output_folder = arguments[0]

        input_files = arguments[1:]
        print(input_files)


    average(*input_files)
    # os.makedirs(output_folder, exist_ok=True)

    # win_times.to_csv(f"{output_folder}/win_times.csv")
    # win_rates.to_csv(f"{output_folder}/win_rates.csv")
    # colt_score.to_csv(f"{output_folder}/colt_scores.csv")
