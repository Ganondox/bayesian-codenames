
from .run_tournament import RunTournament

class RunLearningExperiment:
    def __init__(self, object_manager):
        self.object_manager = object_manager
        self.run_tournament = RunTournament(object_manager)

    def run(self, p=0):
        itr_range = self.object_manager.experiment_settings.iteration_range
        
        self.run_tournament.lower = itr_range[0]
        self.run_tournament.upper = itr_range[1]

        for i in range(itr_range[0], itr_range[1]):
            self.run_tournament.run(i, p)
