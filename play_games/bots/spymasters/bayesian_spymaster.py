import json
from matplotlib import pyplot as plt
import numpy as np
from play_games.bots.ai_components.associator_ai_components.vector_data_cache import VectorDataCache
from play_games.bots.ai_components import vector_utils
from play_games.bots.ai_components.bayesian_components import InternalGuesser
from play_games.bots.bot_settings_obj import BotSettingsObj
from play_games.bots.types import BotType
from play_games.games.enums import Color, GameCondition

class BayesianSpymaster:
    def __init__(self, team, guessers: list[InternalGuesser], prior, noise, samples, name):
        self.team = team
        self.guessers = guessers
        self.prior = prior
        self.noise = noise
        self.samples = samples
        self.name = name
        self.current_guesses = []
        self.previous_guesses = []


        self.posterior = prior.copy()
        self.likelihood = {}
        for g in guessers:
            self.likelihood[g] = {}
        

    def reset(self):
       self.previous_guesses = []
       self.current_guesses = []
       self.posterior = self.prior.copy()

    def initialize(self, bot_settings: BotSettingsObj):
        self.verbose_print = bot_settings.PRINT_LEARNING
        self.log_file = bot_settings.LEARN_LOG_FILE_CM
        self.log = self.log_file.write if self.log_file else (lambda *a, **kw: None)

        self.log(
            f"SPYMASTER: {self.__desc__()}\n"
            f"internal_guessers: {json.dumps([str(g) for g in self.guessers])}\n"
            f"samples: {self.samples}\n"
            f"noise: {self.noise}\n"
            f"prior: {self.prior}\n"
            f"team: {self.team}\n"
            "\n"
        )
    
    def load_dict(self, boardwords: list[str]):
        self.boardwords = boardwords
        self.current_boardwords = boardwords.copy()
        self.reset()
    
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
                    value-=0.5
                case Color.ASSASSIN:
                    value-=9

        return value, np.average(distances_from_clue)
    
    def simulate_guesser(self, words, distances, card_teams, clue_num):
        guess_indcs = sorted(range(len(distances)), key=distances.__getitem__)[:clue_num]

        if clue_num > 3:
            pass

        for guess_i, bw_i in enumerate(guess_indcs):
            if card_teams[words[bw_i]] != self.team:
                break
            
        del guess_indcs[guess_i+1:]
        guess_words = [words[i] for i in guess_indcs]
        guess_dists = [distances[i] for i in guess_indcs]

        return guess_words, guess_dists
    
    def get_possible_clues(self, boardwords):
        possible_clue_words = set()
        for guesser in self.guessers:
            possible_clue_words.update(*[guesser.associations[w] for w in boardwords])
        return list(possible_clue_words)    

    def generate_clue(self, card_teams, boardwords)->tuple[str, list[str]]:
         # We try all clues on the guesser we were given, sampled multiple times to account for noise
        # Whichever one gives the highest expected value is the one we should go for
        # Break ties by minimum average distance to guessed correct clues
        # - g is the game for which a clue is needed
        # - guessed are the cards that have already been guessed
        # - card_teams are the teams for each card
        # - game_log has all the history for this game

        self.previous_guesses = self.current_guesses
        self.current_guesses = []

        player_words = [w for w in boardwords if card_teams[w] == Color.TEAM]

        #update posterior beliefs based on last guess
        if len(self.previous_guesses) > 0:
            guess = self.previous_guesses

            #convert list to number so it can be used as key value
            #
            num = self.toNum(guess, len(self.boardwords)) # + len(guess)
            for guesser in self.guessers:
                if num in self.likelihood[guesser]:
                    self.posterior[guesser] *= self.likelihood[guesser][num]
                # Uniform dirilect prior for estimating likeihood
                    
            total = sum(self.posterior.values())
            self.posterior = {k:v/total for k,v in self.posterior.items()}
        if self.verbose_print: print(self.posterior)
        self.log(f"updated posterior: {json.dumps({str(k):v for k,v in self.posterior.items()})}\n")

        #reset likeihoods
        for guesser in self.guessers:
            for clue_word in self.likelihood[guesser]:
                self.likelihood[guesser][clue_word] = 1; #Uniform dirilect prior for estimating likeihood


        # Track the best clue I find
        best_clue_word = None
        best_clue_val = None
        best_clue_num = None
        best_clue_distance = None

        # How many of my cards are left to guess?  That is the highest
        # clue num that I should try

        temporary_likelihood = {g:{} for g in self.guessers}    
        
        possible_clue_words = self.get_possible_clues(player_words)
        for i, clue_word in enumerate(possible_clue_words, 1):
            if self.verbose_print and i%50==0: print(
                "                                 \r"
                f" {i} / {len(possible_clue_words)}", 
                end='\r'
            )
            for cur_clue_num in range(1, len(player_words) + 1):
                ev = 0
                cur_clue_distance = 0
                #semiconverstive optimization - only try clues that are "good" for at least one guesser, otherwise break num
                good = False
                for guesser in self.guessers:
                    distances_from_clue = [guesser.vectors.distance_word(clue_word, w) for w in boardwords]
                    guess_words, guess_distances = self.simulate_guesser(boardwords, distances_from_clue, card_teams, cur_clue_num)
                    good, cur_clue_distance = self.evaluateGuess(guess_words, guess_distances, card_teams)
                    if good:
                        break
                if not good:
                    break

                for guesser in self.guessers:

                    clueHash = (clue_word, cur_clue_num)
                    if clueHash not in temporary_likelihood:
                        temporary_likelihood[guesser][clueHash] = {}
                    
                    pcv = guesser.vectors[clue_word]
                    bw_embeddings = [guesser.vectors[w] for w in boardwords]
                    _, noisy_distances = vector_utils.get_perturbed_euclid_distances(pcv, bw_embeddings, self.noise, self.samples)

                    for noisy_dists in noisy_distances:
                        guess_words, guess_dists = self.simulate_guesser(boardwords, noisy_dists, card_teams, cur_clue_num)
                        # See how good this guess is
                        # Value = estimated marginal contribution to score at end of game
                        # Cur distance = average distance to the correctly guessed cards
                        value, _ = self.evaluateGuess2(guess_words, guess_dists, card_teams)
                        # doesn't depend on noise
                        ev += value * self.posterior[guesser]

                        #get observation from guess
                        num = self.toNum(guess_words, len(self.boardwords))
                        if num in temporary_likelihood[guesser][clueHash]:
                            temporary_likelihood[guesser][clueHash][num] += 1
                        else:
                            temporary_likelihood[guesser][clueHash][num] = 2 #estimated assuming uniform dirilect prior

                mode_model = max(self.guessers, key=self.posterior.__getitem__)
                cur_clue_distance = sum(
                    d
                    for d in sorted(
                        mode_model.vectors.distance_word(clue_word, w)
                        for w in player_words
                    )[:cur_clue_num]
                ) / cur_clue_num

                # This is better than the best clue by clue val
                if best_clue_word is None or ev > best_clue_val:
                    best_clue_word = clue_word
                    best_clue_num = cur_clue_num
                    best_clue_val = ev
                    best_clue_distance = cur_clue_distance # BUG: This takes the last average distance?

                # Same expected value, but closer distances
                if ev == best_clue_val and cur_clue_distance < best_clue_distance: 
                    best_clue_word = clue_word
                    best_clue_num = cur_clue_num
                    best_clue_val = ev
                    best_clue_distance = cur_clue_distance

                self.likelihood = {g:temporary_likelihood[g][(best_clue_word, best_clue_num)] for g in self.guessers}
        if self.verbose_print: print()
        return (best_clue_word, best_clue_num)
    
    def give_feedback(self, guess: str, *_):
        self.current_guesses.append(guess)

    def __desc__(self):
        return f"{BotType.BAYESIAN_SPYMASTER}:{self.noise}"