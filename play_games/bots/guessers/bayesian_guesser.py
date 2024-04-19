import bisect
import json
from matplotlib import pyplot as plt
import numpy as np
from play_games.bots.ai_components.associator_ai_components.vector_data_cache import VectorDataCache
from play_games.bots.ai_components import vector_utils
from play_games.bots.ai_components.bayesian_components import History, InternalSpymaster, WorldSampler
from play_games.bots.bot_settings_obj import BotSettingsObj
from play_games.bots.types import BotType
from play_games.games.enums import Color, GameCondition
from scipy.stats import norm

EV = {
    Color.TEAM: 1,
    Color.OPPONENT: -1,
    Color.BYSTANDER: -0.5 ,
    Color.ASSASSIN: -9,
}

class BayesianGuesser:

    def __init__(self, team, spymasters: list[InternalSpymaster], prior, noise, samples, name):
        self.team = team
        self.spymasters = spymasters
        self.prior = np.array(list(prior.values()))
        self.noise = noise
        self.samples = samples
        self.guess_threshold = 1 # double
        self.skip_threshold = 0 # double
        self.name = name
        self.guesses_given = []

        self.sampler = WorldSampler()
        self.history = History()
        self.spymaster_posterior = self.prior.copy() # P(m)
        self.guess_iterator = None

    def exp_value(self, color):
        return EV[color]
        
    def reset(self):
        self.guesses_given = []
        self.spymaster_posterior = self.prior.copy()
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
        [s.reset(boardwords) for s in self.spymasters]
        self.reset()

    def guess_clue(self, clue, num_guess, _)->list[str]:
        print(dict(zip(self.spymasters, self.spymaster_posterior)))
        p_prime = 0 # liklihood of observed clue
        samples = self.sampler.sample_states(self.samples)
        state_likelihood = np.ones(len(samples)) # p(w)
        state_posterior = np.full_like(state_likelihood, 1/self.samples)
        spymaster_likelihood = np.ones(len(self.spymasters))

        for clue_t, bw_t, team_left_t in self.history:
            if clue_t == None: continue
            for w_hash, w in enumerate(samples):
                ptw = 0 
                for m_i, m in enumerate(self.spymasters):
                    l_t, _ = m.get_clue(w, bw_t, team_left_t)
                    if self.noise == 0:
                        pt = 1 if l_t == clue_t else 0
                    else:
                        pt = np.prod(norm.pdf(m.vectors[clue_t], loc=m.vectors[l_t], scale=self.noise)) # This would be replaced with a more accurate Voronoi based thingy
                    ptw += pt*self.spymaster_posterior[m_i]
                state_likelihood[w_hash] *= ptw
            state_posterior*=state_likelihood

        for m_i, m in enumerate(self.spymasters):
            for w_hash, w in enumerate(samples):
                l, _ = m.get_clue(w, self.current_boardwords, self.sampler.team_left)
                if self.noise == 0:
                    p =  1 if l == clue else 0
                else:
                    p = np.prod(norm.pdf(m.vectors[clue], loc=m.vectors[l], scale=self.noise))
           
                spymaster_likelihood[m_i] += p * state_posterior[w_hash] 
                state_likelihood[w_hash] += p * self.spymaster_posterior[m_i]
                p_prime += p * state_posterior[w_hash] * self.spymaster_posterior[m_i]

        if p_prime == 0:
            self.history.record(None)
        else:
            self.spymaster_posterior *= spymaster_likelihood
            state_posterior *= state_likelihood
            self.history.record(clue, self.current_boardwords.copy(), self.sampler.team_left)

        if (total:= state_posterior.sum()) != 0:
            state_posterior /= total
        if (total:= self.spymaster_posterior.sum()) != 0:
            self.spymaster_posterior /= total
        
        self.guess_iterator = GuessIterator(self, clue, num_guess, samples, state_posterior)
        return self.guess_iterator
    
    def give_feedback(self, guess: str, color: Color, status: GameCondition):
        self.current_boardwords.remove(guess)
        self.guess_iterator.feedback(guess, color)
        self.guesses_given.append((guess, color))

        if len(self.guesses_given) == self.guess_iterator.num_guess or color != Color.team(self.team):
            self.sampler.update_state(*zip(*self.guesses_given))
            self.guesses_given.clear()

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
    
class GuessIterator:
    def __init__(self, guesser: BayesianGuesser, clue, num_guess, samples, state_posterior):
        self.guesser = guesser
        self.clue = clue
        self.num_guess = num_guess
        self.samples = samples
        self.state_posterior = state_posterior
        self.pr = {}
        self.pb = {}
        self.py = {}
        self.pa = {}


    def feedback(self, guess: str, color: Color):
        if self._get_p_color(color)[guess] == 0:
            self.guesser.spymaster_posterior = self.guesser.prior.copy()
        for i in range(len(self.samples)):
            if self.samples[i] and self.samples[i][guess] != color:
                self.samples[i] = None

    def _get_p_color(self, color):
        match color:
            case _ if color == Color.team(self.guesser.team): return self.pr
            case _ if color == Color.opponent(self.guesser.team): return self.pb
            case Color.BYSTANDER: return self.py
            case Color.ASSASSIN: return self.pa

    def __iter__(self):
        num_guesses_given = 0
        best_spymaster = np.argmax(self.guesser.spymaster_posterior)
        best_spymaster = self.guesser.spymasters[best_spymaster]


        while num_guesses_given <= self.num_guess:
            if self.guesser.sampler.team_left == 0: break
            empty = {w:0 for w in self.guesser.current_boardwords}
            self.pr.update(empty)
            self.pb.update(empty)
            self.py.update(empty)
            self.pa.update(empty)

            sorted_cards = sorted(
                self.guesser.current_boardwords, 
                key=lambda x:best_spymaster.vectors.distance_word(self.clue, x)
            )

            closest_cards = []
            print(len([v for v in self.samples if v is not None]))
            for c in sorted_cards:
                for w_hash, w in enumerate(self.samples):
                    if w is None: continue
                    color = w[c]
                    pc = self._get_p_color(color)
                    pc[c] += self.state_posterior[w_hash]
                
                if self.pr[c] > self.guesser.skip_threshold and len(closest_cards) < self.num_guess-num_guesses_given:
                    closest_cards.append(c)
                # if self.pr[c] >= self.guesser.guess_threshold:
                #     self.pr[c], self.pb[c], self.py[c], self.pa[c] = 1,0,0,0

            for c in closest_cards:
                self.pr[c], self.pb[c], self.py[c], self.pa[c] = 1,0,0,0

            maxv = -np.inf
            maxc = None
            
            for c in sorted_cards:
                if self.pr[c] >= self.guesser.guess_threshold:
                    ev = self.pr[c]*EV[Color.TEAM] + self.pb[c]*EV[Color.OPPONENT] + self.py[c]*EV[Color.BYSTANDER] + self.pa[c]*EV[Color.ASSASSIN]
                    if ev > maxv:
                        maxv = ev
                        maxc = c

            if maxc is None:
                if num_guesses_given > 0: break
                for c in sorted_cards:
                    ev = self.pr[c]*EV[Color.TEAM] + self.pb[c]*EV[Color.OPPONENT] + self.py[c]*EV[Color.BYSTANDER] + self.pa[c]*EV[Color.ASSASSIN]
                    if ev > maxv:
                        maxv = ev
                        maxc = c

            """
            STOP IF:
            out end turn
            ranout of turn aka +1
            or if guesses card on the team
            """

            yield maxc
            num_guesses_given+=1