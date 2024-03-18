def toNum(guess, card_teams):
    radix = len(card_teams)
    num = 0
    exponent = 0
    for c in guess:
        num += c * radix ** exponent
        exponent += 1
    return num

class _BayesianSpymaster():
    def __init__(self, team, guessers, prior, noise, samples, name):
        self.team = team
        self.guessers = guessers
        self.prior = prior
        self.noise = noise
        self.samples = samples
        self.name = name



        self.posterior = prior.copy()
        self.likelihood = {}
        for g in guessers:
            self.likelihood[g] = {}

    def reset(self):
       for guesser in self.guessers:
           guesser.reset()
       self.posterior = self.prior.copy()


    def generateClue(self, game, guessed, card_teams, game_log, verbose=False):
        # We try all clues on the guesser we were given, sampled multiple times to account for noise
        # Whichever one gives the highest expected value is the one we should go for
        # Break ties by minimum average distance to guessed correct clues
        # - g is the game for which a clue is needed
        # - guessed are the cards that have already been guessed
        # - card_teams are the teams for each card
        '''
        from cards to team
        '''
        # - game_log has all the history for this game
        '''
        
        '''

        #update posterior beliefs based on last guess
        if "ObservedGuesses" in game_log and len(game_log["ObservedGuesses"]) > 0:
            guess = game_log["ObservedGuesses"][len(game_log["ObservedGuesses"]) - 1]

            #convert list to number so it can be used as key value
            num = toNum(guess, card_teams)
            for guesser in self.guessers:
                if num in self.likelihood[guesser]:
                    self.posterior[guesser] *= self.likelihood[guesser][num]
                # Uniform dirilect prior for estimating likeihood


        #reset likeihoods
        for guesser in self.guessers:
            for clue in self.likelihood[guesser]:
                self.likelihood[guesser][clue] = 1; #Uniform dirilect prior for estimating likeihood


        # Track the best clue I find
        best_clue_vec = None
        best_clue_val = None
        best_clue_num = None
        best_clue_distance = None

        if verbose:
            print(f"{self.name} CM-K is generating a clue for guessed : {guessed}")

        # How many of my cards are left to guess?  That is the highest
        # clue num that I should try
        guessed_cards = 0
        for gi in guessed:
            if card_teams[gi] == self.team:
                guessed_cards += 1
        my_cards_left = game.start_cards[self.team] - guessed_cards

        # update my internal guesser
        for guesser in self.guessers:
            guesser.updateBeliefsPreTurn(game, game_log)

        for ci, pcv in enumerate(game.possible_clues):

            for cur_clue_num in range(1, my_cards_left + 1):
                ev = 0
                cur_clue_distance = 0
                #semiconverstive optimization - only try clues that are "good" for at least one guesser, otherwise break num
                good = False
                for guesser in self.guessers:
                    cur_clue = (pcv, cur_clue_num)
                    cur_guess = guesser.makeGuess(game, guessed, cur_clue, game_log, verbose)
                    good_guess, cur_clue_distance = evaluateGuess(game, guessed, card_teams, cur_clue, cur_guess, self.team) # Binary feedback if only team cards
                    if(good_guess):
                        good = True
                        break
                if not good:
                    break
                for guesser in self.guessers:
                    for i in range(1, self.samples):
                        #perurb clue
                        vec = perturb_embedding(pcv, self.noise)
                        cur_clue = (vec, cur_clue_num)

                        cur_guess = guesser.makeGuess(game, guessed, cur_clue, game_log, verbose)

                        # See how good this guess is
                        # Value = estimated marginal contribution to score at end of game
                        # Cur distance = average distance to the correctly guessed cards
                        value, cur_clue_distance = evaluateGuess2(game, guessed, card_teams, cur_clue, cur_guess, self.team) # heuristic score and distance 
                        ev += value * self.posterior[guesser]

                        #get observation from guess
                        obs  = []
                        for c in cur_guess:
                            obs.append(c)
                            if card_teams[c] != self.team:
                                break
                        #update likelihood estimate
                        num = toNum(obs, card_teams)
                        if num in self.likelihood[guesser]:
                            self.likelihood[guesser][num] += 1
                        else:
                            self.likelihood[guesser][num] = 2 #estimated assuming uniform dirilect prior


                # This is better than the best clue by clue val
                if best_clue_vec is None or ev > best_clue_val:
                    best_clue_num = cur_clue_num
                    best_clue_vec = pcv
                    best_clue_val = ev
                    best_clue_distance = cur_clue_distance

                # Same expected value, but closer distances
                if ev == best_clue_val and cur_clue_distance < best_clue_distance:
                    best_clue_num = cur_clue_num
                    best_clue_vec = pcv
                    best_clue_val = ev
                    best_clue_distance = cur_clue_distance
        if verbose:
            plt.scatter(best_clue_vec[0], best_clue_vec[1], c='y')
            print(f" {self.name}  >> best clue: ({best_clue_vec}, {best_clue_num})")

        return (best_clue_vec, best_clue_num)

# 