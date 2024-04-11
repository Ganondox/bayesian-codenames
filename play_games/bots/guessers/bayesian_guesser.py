import json
from matplotlib import pyplot as plt
import numpy as np
from play_games.bots.ai_components.associator_ai_components.vector_data_cache import VectorDataCache
from play_games.bots.ai_components import vector_utils
from play_games.bots.ai_components.bayesian_components import ClueHistory, InternalSpymaster, WorldSampler
from play_games.bots.bot_settings_obj import BotSettingsObj
from play_games.bots.types import BotType
from play_games.games.enums import Color, GameCondition

class BayesianGuesser:
    def __init__(self, team, spymasters: list[InternalSpymaster], prior, noise, samples, name):
        self.team = team
        self.spymasters = spymasters
        self.prior = prior
        self.noise = noise
        self.samples = samples
        self.guess_threshold = 1
        self.skip_threshold = 1
        self.name = name
        self.current_guesses = []
        self.previous_guesses = []

        self.sampler = WorldSampler()
        self.history = ClueHistory()
        self.posterior = prior.copy()
        self.spymaster_likelihood = {}
        self.state_likelihood = {}

        for g in spymasters:
            self.spymaster_likelihood[g] = {}
        

    def reset(self):
       self.previous_guesses = []
       self.current_guesses = []
       self.posterior = self.prior.copy()
       self.history.reset()

    def initialize(self, bot_settings: BotSettingsObj):
        self.verbose_print = bot_settings.PRINT_LEARNING
        self.log_file = bot_settings.LEARN_LOG_FILE_CM
        self.log = self.log_file.write if self.log_file else (lambda *a, **kw: None)

        self.log(
            f"GUESSER: {self.__desc__()}\n"
            f"internal_spymasters: {json.dumps([str(g) for g in self.spymasters])}\n"
            f"samples: {self.samples}\n"
            f"noise: {self.noise}\n"
            f"prior: {self.prior}\n"
            f"team: {self.team}\n"
            "\n"
        )
    
    def load_dict(self, boardwords: list[str]):
        self.boardwords = boardwords
        self.current_boardwords = boardwords.copy()
        self.sampler.reset(boardwords)
        self.reset()

    def guess_clue(self, clue, num_guess, prev_guesses)->list[str]:
        self.history.record((clue, num_guess))
        #TODO: does this go after or before?

        p_prime = 0
        samples = self.sampler.sample_states(100)
        sample_hashes = [self.hash_state(s) for s in samples]

        for sample in sample_hashes:
            self.state_likelihood[sample] = 1

        for turn, clue_t in enumerate(self.history):
            if clue == None: continue #??

            for w_hash, w in zip(sample_hashes, samples):
                ptw = 0 # TODO: I think this is wrong
                for m in self.spymasters:
                    mt = m.previous(turn)
                    lt = mt.get_clue(w)
                    pt = None, (clue_t, lt) # WIZARDRY!

                    ptw += pt*self.spymaster_likelihood[m] # TODO: What is this?
                self.state_likelihood[w_hash] *= ptw
        
        # TODO: Finish the rest, get internal spymaster working
        
        return []
    
    def give_feedback(self, guess: str, color: Color, status: GameCondition):
        self.current_guesses.append(guess)
        self.current_boardwords.remove(guess)

    def __desc__(self):
        return f"{BotType.BAYESIAN_GUESSER}:{self.noise}"
    
    def hash_state(self, state, radix=25):
        '''This relies on the order of the boardwords staying constant, so don't change boardwords'''
        num = 0
        exponent = 0
        for c in map(state.__getitem__, self.boardwords):
            num += (c+1) * radix ** exponent
            exponent += 1
        return num

    def toNum(self, guesses, length):
        radix = length
        num = 0
        exponent = 0
        for g in guesses:
            num += hash(g) * radix ** exponent
            exponent += 1
        return num
    
    def hashClue(self, clue_word, clue_num):
        return hash(clue_word) + clue_num
    
    def evaluateGuess(self, guesses, distances_from_clue, card_teams):
        #Evaluate this guess (list of guesses) from the standpoint of team
        # - guessed is the list of previously guessed cards in the game
        # - card_teams is the list of which card is assigned which team
        # - clue is the current clue that was given (clue_value, clue_number)
        # - guess is the guess that we are evaluating
        # - team is the team for which we are evaluating the clue

        if len(guesses) == 0 or card_teams[guesses[-1]] != self.team:
            return False, 0

        return True, np.average(distances_from_clue)

    def evaluateGuess2(self, guesses, distances_from_clue, card_teams):
        # Evaluate this guess (list of guesses) from the standpoint of team
        # - guessed is the list of previously guessed cards in the game
        # - card_teams is the list of which card is assigned which team
        # - clue is the current clue that was given (clue_value, clue_number)
        # - guess is the guess that we are evaluating
        # - team is the team for which we are evaluating the clue
        
        if len(guesses) == 0:
            # print("Evaluating 0 Length Guess")
            return False, 0

        value = -1
        for guess_color in map(card_teams.__getitem__, guesses):
            # If this card isn't our team's, or this card already guessed, then fail
            match guess_color:
                case _ if guess_color == Color.team(self.team):
                    value+=1
                case _ if guess_color == Color.opponent(self.team):
                    value-=1
                case Color.BYSTANDER:
                    pass
                case Color.ASSASSIN:
                    value-=9

        return value, np.average(distances_from_clue)
    
    def get_possible_clues(self, player_words):
        results = set()

        for guesser in self.spymasters:
            for word in player_words:
                results.update(guesser.associations[word])
        
        return results