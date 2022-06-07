from classes import Board
from interfaces.optimization import Optimization
from interfaces.drawer import Drawer
from interfaces.sleeper import Sleeper

from resources.histograms import hist4

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

    def modelling(self, steps: int):
        self.current_steps = self.steps
        while self.current_steps > 0 and not self.sleeper.can_pause():
            self.board.run()
            self.draw()
            self.sleeper.sleep()
            self.current_steps -= 1

    @staticmethod
    def hist_compare(theory, result) -> float:
        theory = hist4
        if len(result) == len(theory):
            eps = sqrt(
                sum(
                    (
                        abs(list(result.values())[i] ** 2 - list(theory.values())[i] ** 2)
                        for i in range(len(theory))
                    )
                )
            )
        elif len(result) > len(theory):
            eps = set()
            for i in range(len(result) - len(theory) + 1):
                eps.add(
                    sqrt(
                        sum(
                            (
                                (list(result.values())[j + i] - list(theory.values())[j]) ** 2
                                for j in range(len(theory))
                            )
                        )
                    )
                )
            eps = min(eps)
        else:
            eps = 1  # TODO: добить до равенства или неравенства

        #koeff1 = polyfit(x=list(result.keys()), y=list(result.values()), deg=1)
        #koeff2 = polyfit(x=list(theory.keys()), y=list(theory.values()), deg=1)

        #eps = sqrt(sum(((koeff1[0] - koeff2[0]) ** 2, (koeff1[1] - koeff2[1]) ** 2))) * eps

        return float(eps)
