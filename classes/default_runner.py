import datetime

from classes import Board
from classes.base_comparator import BaseComparator
from interfaces.drawer import Drawer
from interfaces.sleeper import Sleeper


class DefaultRunner(BaseComparator):
    def __init__(
            self,
            rows: int,
            addprob: float,
            transitprob: float,
            mergeprob: float,
            theory: dict,
            drawer: Drawer,
            sleeper: Sleeper,
            steps: int
    ):
        super().__init__(rows=rows, theory=theory, drawer=drawer, sleeper=sleeper)
        self.board = Board(rows=rows, addprob=addprob, transitprob=transitprob, mergeprob=mergeprob)
        self.steps = steps
        self.current_steps = 0

    def modelling(self):
        if self.theory is None:
            self.current_steps = self.steps
            while self.current_steps > 0:
                self._modelling()
                self.current_steps -= 1
        else:
            super().modelling()

    def optimize(self):
        self.modelling()

    def change_steps(self, new_steps: int):
        self.steps = new_steps

    def result(self):
        _time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        with open(f"results\\BoardAnalysis-{_time}.txt", 'w') as file:
            _dict = self.board.create_bar()
            file.write('WeightAnalysis:\n{')
            for key, value in _dict.items():
                file.write(str(key) + ': ' + str(value) + ', ')
            clusters_info = self.board.clusters_conclusion()
            file.write('}\n\nClusterAnalysis:\n' + clusters_info)
