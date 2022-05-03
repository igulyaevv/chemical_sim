from interfaces.optimization import Optimization


class CoordinateDescent(Optimization):
    def __init__(self, start_add, start_transit, start_merge, iter_count, step):
        self.probs = [start_add, start_transit, start_merge]
        self._hist = []
        self.iter_count = iter_count
        self.step = step

    def optimize(self, objective):
        for i in range(self.iter_count):
            current_optimize = []
            for prob in range(len(self.probs)):
                if self.probs[prob] - self.step >= 0:
                    self.probs[prob] -= self.step
                else:
                    continue

                board = Board(10, self.probs[0], self.probs[1], self.probs[2])
                # здесь передаем вызов UI, ждем завершения и сравниваем результаты
                value = gist_compare(board.create_bar(), theory)
                current_optimize.append((self.probs[0], self.probs[1], self.probs[2], value))
                self.probs[prob] += self.step

            values = [value[3] for value in current_optimize]
            if len(values) == 0:
                print('variables too little')
                break

            value = min(values)
            if len(self.hist) > 0 and value >= self.hist[-1][3]:
                print('value has not changed')
                break

            for opt in current_optimize:
                if value == opt[3]:
                    self.hist.append(opt)
                    self.probs[0] = opt[0]
                    self.probs[1] = opt[1]
                    self.probs[2] = opt[2]
                    break
            current_optimize.clear()

            if value <= 0:
                print('optimized')
                break

    @property
    def hist(self):
        return self._hist  # TODO: переделать вывод
