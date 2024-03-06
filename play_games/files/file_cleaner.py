import os
import re

class FileCleaner:
    def __init__(self, object_manager):
        self.object_manager = object_manager

    def clean_learn_logs(self):
        cm_learn_logs = self.object_manager.experiment_paths.learn_log_filepaths_cm 
        g_learn_logs = self.object_manager.experiment_paths.learn_log_filepaths_g

        #clean all of the cm learn logs 
        
        for l in cm_learn_logs:
            new_lines = []
            count = 0
            try:
                with open(l, 'r') as f:
                    for line in f:
                        elements = line.split(' ')
                        if elements[0] == "STARTING":
                            count += 1 
                        if  count > 18:
                            break
                        #otherwise we write it to our new file 
                        new_lines.append(line)
            except:
                continue

            #swithch this out for the same file name 
            with open(l, 'w+') as f:
                for line in new_lines:
                    f.write(line)
        
        #now we do a similar thing for g 
        
        for l in g_learn_logs:
            new_lines = []
            count = 0 
            skip = False 
            try:
                with open(l, 'r') as f:
                    for line in f:
                        elements = line.split(' ')
                        if elements[0] == "STARTING" and skip == False:
                            skip = True
                            count += 1 
                        elif elements[0] == "STARTING" and skip == True:
                            skip = False

                        if  count % 2 == 0:
                            continue
                        #otherwise we write it to our new file 
                        new_lines.append(line)
            except:
                continue

            with open(l, 'w+') as f:
                for line in new_lines:
                    f.write(line)
    
    def delete_small_files(self):
        round_logs_dir = self.object_manager.experiment_paths.round_logs_dir_path
        learn_logs_dir = self.object_manager.experiment_paths.learn_logs_dir_path

        #loop through all of the round logs and delete all of the files less than 1 MB 
        for log in os.listdir(round_logs_dir):
            p = os.path.join(round_logs_dir, log)
            file_size = os.path.getsize(p)
            if file_size < 10000000: #megabyte 
                os.remove(p)
            
        
        for log in os.listdir(learn_logs_dir):
            p = os.path.join(learn_logs_dir, log)
            file_size = os.path.getsize(p)
            if file_size < 1000000: 
                os.remove(p)

    def delete_files(self, one, two, three):
        if os.path.exists(one):
            os.remove(one)
        if os.path.exists(two):
            os.remove(two)
        if os.path.exists(three):
            os.remove(three)

    def delete_unmatched_files(self):
        round_logs = self.object_manager.experiment_paths.round_log_filepaths
        cm_learn_logs = self.object_manager.experiment_paths.learn_log_filepaths_cm 
        g_learn_logs = self.object_manager.experiment_paths.learn_log_filepaths_g
        pattern = r"_(\d+).txt"

        #I'll just assume there is a learn log of each type for each experiment for now
        for rl, cll, gll in zip(round_logs, cm_learn_logs, g_learn_logs):
            #we need to check that the files all exist (or don't) and that they are the same 
            #check if they don't all have same existence status
            if not (os.path.exists(rl) == os.path.exists(cll) == os.path.exists(gll)):
                self.delete_files(rl, cll, gll)
                continue

            #if they don't exist, continue 
            if not os.path.exists(rl):
                continue

            if os.path.getsize(rl) == 0 or os.path.getsize(gll) == 0 or os.path.getsize(cll) == 0:
                if not (os.path.getsize(rl) == os.path.getsize(gll) == os.path.getsize(cll)):
                    self.delete_files(rl, gll, cll)
                    continue
            