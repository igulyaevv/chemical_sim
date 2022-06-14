from classes.base_comparator import BaseComparator
from classes import Board
from interfaces.drawer import Drawer
from interfaces.sleeper import Sleeper


class CoordinateDescent(BaseComparator):
    def __init__(
            self,
            rows: int,
            addprob: float,
            transitprob: float,
            mergeprob: float,
            drawer: Drawer,
            sleeper: Sleeper,
            theory: dict,
            multiplier: float
    ):
        super().__init__(rows=rows, drawer=drawer, sleeper=sleeper, theory=theory)
        self.probs = [addprob, transitprob, mergeprob]
        self._hist = []
        self.multiplier = multiplier
        self.first_trial = True

    def optimize(self):
        current_optimize = []
        for prob in range(len(self.probs)):
            if self.probs[prob] - self.multiplier >= 0:
                self.probs[prob] -= self.multiplier
            else:
                continue

            if self.first_trial:
                self.first_trial = False
            else:
                self.board = Board(self.rows, self.probs[0], self.probs[1], self.probs[2])

            self.modelling()
            value = self.hist_compare(self.theory, self.board.create_bar())
            current_optimize.append((self.probs[0], self.probs[1], self.probs[2], value))
            self.probs[prob] += self.multiplier
        values = [value[3] for value in current_optimize]
        if len(values) == 0:
            print('variables too little')
        value = min(values)
        if len(self._hist) > 0 and value >= self._hist[-1][3]:
            print('value has not changed')
        for opt in current_optimize:
            if value == opt[3]:
                self._hist.append(opt)
                self.probs[0] = opt[0]
                self.probs[1] = opt[1]
                self.probs[2] = opt[2]
                break
        current_optimize.clear()
        if value <= 0:
            print('optimized')

    def result(self):
        return self._hist  # TODO: переделать вывод
