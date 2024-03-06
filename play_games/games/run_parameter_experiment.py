
from .run_learning_experiment import RunLearningExperiment
from .run_tournament import RunTournament
import copy

class RunParameterExperiment:
    def __init__(self, object_manager):
        # self.object_manager = object_manager
        # self.run_learning_experiment = RunLearningExperiment(object_manager)
        self.object_manager = object_manager
        self.run_tournament = RunTournament(object_manager)

    def run(self):
        variables = self.object_manager.experiment_settings.variable_space
        # We extract the iteration range and then set it to size 1
        self.object_manager.experiment_settings.iteration_range = [0, 1]

        for i in range(len(variables)):
            self.run_tournament.run(0, i)