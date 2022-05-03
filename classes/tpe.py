import optuna

from interfaces.optimization import Optimization


class TPE(Optimization):
    def __init__(self):
        self.study = optuna.create_study()

    @staticmethod
    def get_next_params(trial):
        add = trial.suggest_float("add", 0, 1)
        merge = trial.suggest_float("merge", 0, 1)
        transit = trial.suggest_float("transit", 0, 1)

        board = Board(10, add, transit, merge)
        # здесь передаем вызов UI, ждем завершения и сравниваем результаты

        return gist_compare(board.create_bar(), theory)

    def optimize(self, objective):
        self.study.optimize(lambda trial: self.get_next_params(trial))

    @property
    def hist(self):
        return self.study.get_trials()  # TODO: сделать преобразование вывода