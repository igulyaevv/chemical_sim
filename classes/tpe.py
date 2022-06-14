import optuna

from classes.base_comparator import BaseComparator
from classes.board import Board
from interfaces.drawer import Drawer
from interfaces.sleeper import Sleeper


class TPE(BaseComparator):
    def __init__(self, rows: int, theory: dict, drawer: Drawer, sleeper: Sleeper):
        super().__init__(rows=rows, theory=theory, drawer=drawer, sleeper=sleeper)
        self.study = optuna.create_study()
        self.hists = {}

    def _get_next_params(self, trial):
        if self.board:
            number = self.study.get_trials()[-1].number
            self.hists[number] = self.board.create_bar()
        add = trial.suggest_float("add", 0, 1)
        transit = trial.suggest_float("transit", 0, 1)
        merge = trial.suggest_float("merge", 0, 1)
        self.board = Board(self.rows, add, transit, merge)

        self.modelling()

        return self.hist_compare(self.theory, self.board.create_bar())

    def optimize(self):
        self.study.optimize(lambda trial: self._get_next_params(trial), n_trials=1)

    def result(self):
        result = []
        for trial in self.study.get_trials():
            result.append(
                {
                    'number': trial.number,
                    'value': trial.values[-1],
                    'params': {
                        'add': trial.params.get('add'),
                        'transit': trial.params.get('transit'),
                        'merge': trial.params.get('merge')
                    },
                    'hist': self.hists.get(trial.number)
                }
            )
        return result
