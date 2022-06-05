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
