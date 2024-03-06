'''
This will contain an associator that will be passed in it's instantiations. 
This will load the board and calculate a frequency dict
'''
from bots.ai_components.associator_ai_components.associator_data_cache import AssociatorDataCache

class Associator:
    def __init__(self, n, path, f):
        self.datacache = AssociatorDataCache(path)
        self.datacache.load_cache(n)
        self.board_dict = {}
        self.freq_dict = {}
        self.ext_board_dict = {}
        self.association_location_dict = {}
        self.log_file = f
    
    def load_dict(self, boardwords):
        self.board_dict.clear()
        for word in boardwords:
            self.board_dict[word] = self.datacache.get_associations(word)
        
        self.freq_dict.clear()

        for key in self.board_dict.keys():
            wordset = self.board_dict[key]
            for word in wordset:
                if word in self.freq_dict:
                    self.freq_dict[word] += 1
                else:
                    self.freq_dict[word] = 1
    
    def load_ext_dict(self, board_lst):
        for word in board_lst:
            self.ext_board_dict[word] = self.datacache.get_ext_associations(word)
    
    def give_feedback(self, val1, val2):
        pass
    