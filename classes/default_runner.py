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

    def _modelling(self):
        self.board.run()
        self.draw()
        self.sleeper.sleep()

    def modelling(self):
        if self.theory is None:
            self.current_steps = self.steps
            while self.current_steps > 0 and not self.sleeper.can_pause():
                self._modelling()
                self.current_steps -= 1
        else:
            while len(self.board.create_bar()) <= len(self.theory) and not self.sleeper.can_pause():
                self._modelling()

    def optimize(self):
        self.modelling()

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
