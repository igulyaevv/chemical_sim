import optuna

from classes.base_comparator import BaseComparator
from classes.board import Board
from interfaces.drawer import Drawer
from interfaces.sleeper import Sleeper


class TPE(BaseComparator):
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

        self.study = optuna.create_study()
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
        self.first_trial = True

    def _get_next_params(self, trial):
        if self.current_steps == 0:
            if self.first_trial:
                self.first_trial = False
            else:
                add = trial.suggest_float("add", 0, 1)
                merge = trial.suggest_float("merge", 0, 1)
                transit = trial.suggest_float("transit", 0, 1)
                self.board = Board(self.rows, add, transit, merge)

        self.modelling(self.steps)

        if self.sleeper.can_pause():
            return  # TODO: перевести в паузу потока

        return self.hist_compare(self.theory, self.board.create_bar())

    def optimize(self):
        self.study.optimize(lambda trial: self._get_next_params(trial), n_trials=1)

    def hist(self):
        return self.study.get_trials()  # TODO: сделать преобразование вывода
