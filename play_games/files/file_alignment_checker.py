import os 
import re
from play_games.utils.object_manager import ObjectManager

from play_games.paths import file_paths

class FileAlignmentChecker:
    def __init__(self, object_manager: ObjectManager):
        self.paths = object_manager.experiment_paths 
    
    def check_alignment(self):
        round_logs = self.paths.round_log_filepaths
        cm_learn_logs = self.paths.learn_log_filepaths_cm 
        g_learn_logs = self.paths.learn_log_filepaths_g
        pattern = r"_(\d+).txt"

        c = 0
        #I'll just assume there is a learn log of each type for each experiment for now
        if len(g_learn_logs) > 0 and len(cm_learn_logs) > 0:
            for rl, cll, gll in zip(round_logs, cm_learn_logs, g_learn_logs):
                #we need to check that the files all exist (or don't) and that they are the same 
                #check if they don't all have same existence status
                if not (os.path.exists(rl) == os.path.exists(cll) == os.path.exists(gll)):
                    return False

                #if they don't exist, continue 
                if not os.path.exists(rl):
                    continue

                if os.path.getsize(rl) == 0 or os.path.getsize(gll) == 0 or os.path.getsize(cll) == 0:
                    if not (os.path.getsize(rl) == os.path.getsize(gll) == os.path.getsize(cll)):
                        return False
                
                #now we check that the number is the same among all of the files 
                n1 = int(re.search(pattern, rl).group(1))
                n2 = int(re.search(pattern, cll).group(1))
                n3 = int(re.search(pattern, gll).group(1))
                if not (n1 == n2 == n3):
                    return False
                c += 1
        elif len(g_learn_logs) > 0:
            pass 
        elif len(cm_learn_logs) > 0:
            pass 
        else:
            for rl in round_logs:
                if os.path.exists(rl) and os.path.getsize(rl) > 0:
                    c += 1

        print("count:", c)
            
        
        #if we survive the gauntlet, we return True
        return True 
