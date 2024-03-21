from matplotlib import pyplot as plt
import numpy as np
from play_games.bots.ai_components.associator_ai_components.vector_data_cache import VectorDataCache
from play_games.bots.ai_components import vector_utils
from play_games.bots.ai_components.bayesian_components import InternalGuesser
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

    def initialize(self, _):
        pass
    
    def load_dict(self, boardwords: list[str]):
        self.boardwords = boardwords
        self.reset()
    
    def toNum(self, guesses, length):
        radix = length
        num = 0
        exponent = 0
        for g in guesses:
            num += hash(g) * radix ** exponent
            exponent += 1
        return num
    
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
    
    def get_possible_clues(self, player_words):
        results = set()

        for guesser in self.guessers:
            for word in player_words:
                results.update(guesser.associations[word])
        
        return results
        

    def generate_clue(self, player_words, prev_guesses, opponent_words, assassin_word, bystander_words, verbose=True)->tuple[str, list[str]]:
         # We try all clues on the guesser we were given, sampled multiple times to account for noise
        # Whichever one gives the highest expected value is the one we should go for
        # Break ties by minimum average distance to guessed correct clues
        # - g is the game for which a clue is needed
        # - guessed are the cards that have already been guessed
        # - card_teams are the teams for each card
        # - game_log has all the history for this game

        boardwords = [b for b in self.boardwords if b not in prev_guesses]
        self.previous_guesses = self.current_guesses
        self.current_guesses = []

        card_teams = {}
        for word in player_words:
            card_teams[word] = Color.team(self.team)
        for word in opponent_words:
            card_teams[word] = Color.opponent(self.team)
        for word in bystander_words:
            card_teams[word] = Color.BYSTANDER
        card_teams[assassin_word] = Color.ASSASSIN

        #update posterior beliefs based on last guess
        if len(self.previous_guesses) > 0:
            guess = self.previous_guesses

            #convert list to number so it can be used as key value
            #
            num = self.toNum(guess, len(self.boardwords)) # + len(guess)
            # BUG: This relies on the current boardwords whereas last round the boardwords where different?
            for guesser in self.guessers:
                if num in self.likelihood[guesser]:
                    self.posterior[guesser] *= self.likelihood[guesser][num]
                # Uniform dirilect prior for estimating likeihood
                    
            total = sum(self.posterior.values())
            self.posterior = {k:v/total for k,v in self.posterior.items()}
        print(self.posterior)


        #reset likeihoods
        for guesser in self.guessers:
            for clue in self.likelihood[guesser]:
                self.likelihood[guesser][clue] = 1; #Uniform dirilect prior for estimating likeihood


        # Track the best clue I find
        best_clue_word = None
        best_clue_val = None
        best_clue_num = None
        best_clue_distance = None

        if verbose:
            print(f"{self.name} CM-K is generating a clue for guessed : {prev_guesses}")

        # How many of my cards are left to guess?  That is the highest
        # clue num that I should try
        my_cards_left = len(player_words)

        possible_clue_words = self.get_possible_clues(player_words)
        for i, clue in enumerate(possible_clue_words, 1):
            print(
                "                                 \r"
                f" {i} / {len(possible_clue_words)}", 
                end='\r'
            )
            for cur_clue_num in range(1, my_cards_left + 1):
                ev = 0
                cur_clue_distance = 0
                #semiconverstive optimization - only try clues that are "good" for at least one guesser, otherwise break num
                good = False
                for guesser in self.guessers:
                    distances_from_clue = [guesser.vectors.distance_word(clue, w) for w in boardwords]
                    guess_words, guess_distances = self.simulate_guesser(boardwords, distances_from_clue, card_teams, cur_clue_num)
                    good, cur_clue_distance = self.evaluateGuess(guess_words, guess_distances, card_teams)
                    if good:
                        break
                if not good:
                    break

                for guesser in self.guessers:
                    
                    pcv = guesser.vectors[clue]
                    bw_embeddings = [guesser.vectors[w] for w in boardwords]
                    _, noisy_distances = vector_utils.get_perturbed_euclid_distances(pcv, bw_embeddings, self.noise, self.samples)

                    for noisy_dists in noisy_distances:
                        guess_words, guess_dists = self.simulate_guesser(boardwords, noisy_dists, card_teams, cur_clue_num)
                        # See how good this guess is
                        # Value = estimated marginal contribution to score at end of game
                        # Cur distance = average distance to the correctly guessed cards
                        value, cur_clue_distance = self.evaluateGuess2(guess_words, guess_dists, card_teams)
                        cur_clue_distance = sum(guesser.vectors.distance_word(clue, w) for w in boardwords)
                        # doesn't depend on noise
                        ev += value * self.posterior[guesser]

                        #get observation from guess
                        num = self.toNum(guess_words, len(self.boardwords))
                        if num in self.likelihood[guesser]:
                            self.likelihood[guesser][num] += 1
                        else:
                            self.likelihood[guesser][num] = 2 #estimated assuming uniform dirilect prior


                # This is better than the best clue by clue val
                if best_clue_word is None or ev > best_clue_val:
                    best_clue_word = clue
                    best_clue_num = cur_clue_num
                    best_clue_val = ev
                    best_clue_distance = cur_clue_distance # BUG: This takes the last average distance?

                # Same expected value, but closer distances
                if ev == best_clue_val and cur_clue_distance < best_clue_distance: 
                    best_clue_word = clue
                    best_clue_num = cur_clue_num
                    best_clue_val = ev
                    best_clue_distance = cur_clue_distance
        print()
        return (best_clue_word, ['target']*best_clue_num)
    
    def give_feedback(self, guess: str, *_):
        self.current_guesses.append(guess)