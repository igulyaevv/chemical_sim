import datetime
import json

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

    def _func(self, addprob: float, transitprob: float, mergeprob: float):
        self.board = Board(self.rows, addprob, transitprob, mergeprob)
        self.modelling()

        return self.hist_compare(self.theory, self.board.create_bar()), self.board.create_bar()

    @staticmethod
    def _fixed_step(probs: list, it: int, func, step: float):
        x_ = list(probs)
        x1 = list(probs)

        if probs[it] - step > 0.0:
            x_[it] = probs[it] - step
        if probs[it] + step <= 1.0:
            x1[it] = probs[it] + step

        if x1 == probs and x_ == probs:
            return

        f_, hist_ = func(x_[0], x_[1], x_[2])
        f1, hist1 = func(x1[0], x1[1], x1[2])

        if f_ > f1:
            probs[it] = x1[it]
            return f1, hist_
        else:
            probs[it] = x_[it]
            return f_, hist1

    def optimize(self):
        for i in range(len(self.probs)):
            value, hist = self._fixed_step(probs=self.probs, it=i, func=self._func, step=self.multiplier)
            if i == 2:
                self._hist.append((self.probs[0], self.probs[1], self.probs[2], value, hist))

    def result(self):
        _time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        result = []
        num = 0
        for trial in self._hist:
            result.append(
                {
                    'number': num,
                    'value': trial[3],
                    'params': {
                        'add': trial[0],
                        'transit': trial[1],
                        'merge': trial[2]
                    },
                    'hist': trial[4]
                }
            )
            num += 1

        with open(f"results\\CDOptimization-{_time}.txt", 'w') as file:
            for trial in result:
                trial = json.dumps(trial)
                file.write(trial + '\n')

        return result
