from classes import Board
from interfaces.optimization import Optimization
from interfaces.drawer import Drawer
from interfaces.sleeper import Sleeper

from math import sqrt

from numpy.polynomial.polynomial import polyfit


class BaseComparator(Optimization):

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
        self.rows = rows
        self.theory = theory
        self.sleeper = sleeper
        self.drawer = drawer
        self.board = Board(rows=self.rows, addprob=addprob, transitprob=transitprob, mergeprob=mergeprob)
        self.steps = steps
        self.current_steps = 0

    def optimize(self):
        pass

    def result(self):
        pass

    def draw(self):
        self.drawer.prepare_draw()
        self.board.draw(self.drawer)
        self.drawer.draw_bar(self.board.create_bar())
        self.drawer.complete_draw()

    def modelling(self):
        pass

    @staticmethod
    def hist_compare(theory, result) -> float:
        sorted_theory = sorted(theory.items(), key=lambda x: x[0])
        sorted_result = sorted(result.items(), key=lambda x: x[0])
        values_theory = list(i[1] for i in sorted_theory)
        values_result = list(i[1] for i in sorted_result)

        eps = set()
        for i in range(len(values_result) - len(values_theory) + 1):
            eps.add(
                sum((values_result[j + i] ** 2 - values_theory[j] ** 2 for j in range(len(theory))))
            )
        eps = min(eps)

        eps = sqrt(abs(eps))

        koeff1 = polyfit(x=list(result.keys()), y=list(result.values()), deg=1)
        koeff2 = polyfit(x=list(theory.keys()), y=list(theory.values()), deg=1)

        # TODO: вырбать вариант расчета отклонения eps = sqrt(sum(((koeff1[0] - koeff2[0]) ** 2, (koeff1[1] - koeff2[1]) ** 2))) * eps
        eps = abs(koeff1[1] - koeff2[1]) * eps

        return eps
