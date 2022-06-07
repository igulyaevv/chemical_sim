import datetime

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
            steps: int):

        super().__init__(
            rows=rows,
            addprob=addprob,
            transitprob=transitprob,
            mergeprob=mergeprob,
            theory=theory,
            drawer=drawer,
            sleeper=sleeper,
            steps=steps
        )

    def optimize(self):
        self.modelling(self.steps)

    def change_steps(self, new_steps: int):
        self.steps = new_steps

    def result(self):
        _time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        with open(f"results\\WeightAnalysis-{_time}.txt", 'w') as file:
            _dict = self.board.create_bar()
            for key in sorted(_dict.keys()):
                for i in range(_dict[key]):
                    file.write(str(key) + ' ')
        self.board.clusters_conclusion(_time)
