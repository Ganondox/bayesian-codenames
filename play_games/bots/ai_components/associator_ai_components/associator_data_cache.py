'''
This file will contain associations from the json file. You will pass in a filepath
'''

import json

__file_cache = dict()

def _pull_assocs_from_cache(filepath):
    if filepath not in __file_cache:
        with open(filepath) as f: __file_cache[filepath] = json.load(f).items()
    return __file_cache[filepath]


class AssociatorDataCache:
    def __init__(self, filepath):
        self.filepath = filepath
        self.associations = {}
        self.wordlist = []
    
    def load_cache(self,n):
        self.associations = {word:assocs[:n] for word, assocs, in _pull_assocs_from_cache(self.filepath)}
        self.wordlist = list(self.associations.keys())
    
    def __getitem__(self, word):
        return self.associations[word]
    
    def get_associations(self, word):
        return self.associations[word]
    
    def get_wordlist(self):
        return self.wordlist