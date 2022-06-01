from . import Cell
from . import Cluster

import random
import statistics

from interfaces.drawer import Drawer
from interfaces.drawable import Drawable

from resources.constants import RESIZE, Status, status_definition, Modes

random.seed()


class Board(Drawable):
    def __init__(
            self,
            rows: int,
            addprob: float,
            transitprob: float,
            mergeprob: float,
            current_mode: Modes = Modes.CONST
    ):
        self._rows = rows
        self._columns = RESIZE
        self._place = [[-1] * self._columns for _ in range(self._rows)]
        self._clusters = {}
        self._current_mode = current_mode
        self._create_atom = addprob
        self._transit_atom = transitprob
        self._merge_cluster = mergeprob
        self._atoms_count = 0

    @property
    def rows(self) -> int:
        return self._rows

    def resize(self) -> None:
        """Расширяет сетку в одной размерности на величину константы RESIZE."""

        for row in self._place:
            row += [-1] * RESIZE
        self._columns += RESIZE

    def add_atom(self, row: int) -> Cell:
        """Добавляет в данную строку атом. Если данная строка заполнена - производит расширение сетки."""

        j = self._place[row].index(-1) if -1 in self._place[row] else self._columns
        if j >= self._columns:
            self.resize()
        self._place[row][j] = 0

        return Cell(row, j)

    def atom_transition(self, current: Cell) -> Cell:
        """Осуществляет переход атома в соседнюю ячейку на поверхности. Выбирает два пути: вверх или вниз вдоль
        поверхности. Может переместить на свободную ячейку, либо поверх другого атома. В случае, если оба направления
        заблокированы, возвращает входной параметр - т.е. не осуществляет перемещения."""

        rand = random.choice((True, False))
        is_up = True if rand else False

        self._place[current.x][current.y] = -1

        if is_up and current.x - 1 >= 0:
            current = self.add_atom(current.x - 1)
        elif not is_up and current.x + 1 < self._rows:
            current = self.add_atom(current.x + 1)

        return current

    def check_cluster(self, current: Cell, candidates: list, temp_place: list) -> None:
        """Рекурсивная функция поиска кандидатов для добавления в существующие кластеры или для создания нового"""

        x = current.x
        y = current.y

        if self._place[x][y] == -1:
            temp_place[x][y] = 1
            return
        elif temp_place[x][y] == 1:
            return

        temp_place[x][y] = 1

        cur_val = self._place[x][y]

        if x - 1 >= 0 and x + 1 < self._rows and y - 1 >= 0 and y + 1 < self._columns and \
                self._place[x - 1][y] == cur_val and self._place[x + 1][y] == cur_val and \
                self._place[x][y - 1] == cur_val and self._place[x][y + 1] == cur_val and \
                self._place[x + 1][y + 1] == cur_val and self._place[x - 1][y + 1] == cur_val and \
                self._place[x + 1][y - 1] == cur_val and self._place[x - 1][y - 1] == cur_val:
            return

        candidates.append(Cell(x, y))

        if x - 1 >= 0:
            self.check_cluster(Cell(x - 1, y), candidates, temp_place)

        if x + 1 < self._rows:
            self.check_cluster(Cell(x + 1, y), candidates, temp_place)

        if y - 1 >= 0:
            self.check_cluster(Cell(x, y - 1), candidates, temp_place)

        if y + 1 < self._columns:
            self.check_cluster(Cell(x, y + 1), candidates, temp_place)

        if x - 1 >= 0 and y - 1 >= 0:
            self.check_cluster(Cell(x - 1, y - 1), candidates, temp_place)

        if x + 1 < self._rows and y - 1 >= 0:
            self.check_cluster(Cell(x + 1, y - 1), candidates, temp_place)

        if x - 1 >= 0 and y + 1 < self._columns:
            self.check_cluster(Cell(x - 1, y + 1), candidates, temp_place)

        if x + 1 < self._rows and y + 1 < self._columns:
            self.check_cluster(Cell(x + 1, y + 1), candidates, temp_place)

    def create_cluster(self, current: Cell) -> None:
        """Создает кластерновый кластер, если в окрестности есть 4 свободных атома, либо добавляет свободные атомы к
        существующим кластера, либо производит слияние кластеров"""

        temp_place = [[0] * self._columns for _ in range(self._rows)]
        candidates = []
        self.check_cluster(current, candidates, temp_place)

        min_clusternumber = 0
        for atom in candidates:
            if self._place[atom.x][atom.y] != 0:
                if min_clusternumber == 0:
                    min_clusternumber = self._place[atom.x][atom.y]
                else:
                    min_clusternumber = min(min_clusternumber, self._place[atom.x][atom.y])

        if min_clusternumber == 0:
            if len(candidates) >= 4:
                new_cluster = Cluster(limiter=self._rows)
                for atom in candidates:
                    new_cluster.add_atom(atom)
                self._clusters[new_cluster.number] = new_cluster
                self.cluster_coloring(self._clusters.get(new_cluster.number))
        else:
            merging = set()
            for atom in candidates:
                if self._place[atom.x][atom.y] == min_clusternumber:
                    continue
                elif self._place[atom.x][atom.y] != 0:
                    merging.add(self._place[atom.x][atom.y])
                else:
                    new_found = -1
                    if atom.x - 1 >= 0 and self._place[atom.x - 1][atom.y] > 0:
                        new_found = self._place[atom.x - 1][atom.y]

                    if atom.x + 1 < self._rows and self._place[atom.x + 1][atom.y] > 0:
                        new_found = self._place[atom.x + 1][atom.y]

                    if atom.y - 1 >= 0 and self._place[atom.x][atom.y - 1] > 0:
                        new_found = self._place[atom.x][atom.y - 1]

                    if atom.y + 1 < self._columns and self._place[atom.x][atom.y + 1] > 0:
                        new_found = self._place[atom.x][atom.y + 1]

                    if atom.x - 1 >= 0 and atom.y - 1 >= 0 and self._place[atom.x - 1][atom.y - 1] > 0:
                        new_found = self._place[atom.x - 1][atom.y - 1]

                    if atom.x - 1 >= 0 and atom.y + 1 < self._columns and self._place[atom.x - 1][atom.y + 1] > 0:
                        new_found = self._place[atom.x - 1][atom.y + 1]

                    if atom.x + 1 < self._rows and atom.y - 1 >= 0 and self._place[atom.x + 1][atom.y - 1] > 0:
                        new_found = self._place[atom.x + 1][atom.y - 1]

                    if atom.x + 1 < self._rows and atom.y + 1 < self._columns and self._place[atom.x + 1][atom.y + 1] > 0:
                        new_found = self._place[atom.x + 1][atom.y + 1]

                    if new_found != -1:
                        self._clusters[new_found].add_atom(atom)
                        self.cluster_coloring(self._clusters.get(new_found))
            if len(merging) > 0:
                self.cluster_merger([i for i in merging] + [min_clusternumber])  # TODO: Сделать список слияния возвращаемым, чтобы использовать его вне метода, в управляющем методе

    def check_cluster_for_clusters(self, found: int) -> None:
        """Определяет, есть ли в окрестности данного кластера другие кластеры или свободные атомы.
        Если есть, то запускает процедуру создание кластера (create_cluster)"""

        cluster_number = self._clusters[found].number
        for i in range(self._clusters[found].size()):
            x = self._clusters[found].atoms[i].x
            y = self._clusters[found].atoms[i].y
            if 0 <= x < self._rows and 0 <= y < self._columns:
                if (x - 1 >= 0 and self._place[x - 1][y] != cluster_number and self._place[x - 1][y] != -1 or
                        x + 1 < self._rows and self._place[x + 1][y] != cluster_number and self._place[x + 1][y] != -1 or
                        y - 1 >= 0 and self._place[x][y - 1] != cluster_number and self._place[x][y - 1] != -1 or
                        y + 1 < self._columns and self._place[x][y + 1] != cluster_number and self._place[x][y + 1] != -1 or
                        x - 1 >= 0 and y - 1 >= 0 and self._place[x - 1][y - 1] != cluster_number and self._place[x - 1][
                            y - 1] != -1 or
                        x - 1 >= 0 and y + 1 < self._columns and self._place[x - 1][y + 1] != cluster_number and
                        self._place[x - 1][y + 1] != -1 or
                        x + 1 < self._rows and y - 1 >= 0 and self._place[x + 1][y - 1] != cluster_number and
                        self._place[x + 1][y - 1] != -1 or
                        x + 1 < self._rows and y + 1 < self._columns and self._place[x + 1][y + 1] != cluster_number and
                        self._place[x + 1][y + 1] != -1):
                    self.create_cluster(self._clusters[found].atoms[i])
                    return

    def cluster_uncoloring(self, cluster: Cluster) -> None:
        """Убирает атомы кластера с сетки"""

        for item in cluster.atoms:
            if 0 <= item.x < self._rows and 0 <= item.y < self._columns:
                self._place[item.x][item.y] = -1

    def cluster_coloring(self, cluster: Cluster) -> None:
        """Отрисовывает атомы кластера на сетку"""

        for item in cluster.atoms:
            if item.y >= self._columns:
                self.resize()
            if 0 <= item.x < self._rows and 0 <= item.y < self._columns:
                self._place[item.x][item.y] = cluster.number

    def cluster_merger(self, candidates: list) -> None:
        """Процедура слияние кластеров. Если кластеров > 2, тогда все кластеры сливаются в один, в противном случае
        на основе генератора случайных чисел либо сливает кластеры в один, либо же отталкивает друг от друга
        в зависимости от размеров кластера"""

        if len(candidates) > 2:
            for i in range(len(candidates) - 1):
                self._clusters[candidates[-1]].merger(self._clusters[candidates[i]])
                self._clusters[candidates[i]].status = Status.MERGING
                self.cluster_uncoloring(self._clusters[candidates[i]])
            self.cluster_coloring(self._clusters.get(candidates[-1]))
        else:
            randmerge = random.random()
            if randmerge <= self._merge_cluster or self._clusters[candidates[0]].status == Status.ON_SURFACE or \
                    self._clusters[candidates[1]].status == Status.ON_SURFACE:
                self._clusters[candidates[1]].merger(self._clusters[candidates[0]])
                self.cluster_uncoloring(self._clusters[candidates[0]])
                self.cluster_coloring(self._clusters[candidates[1]])
                self._clusters[candidates[0]].status = Status.MERGING
            else:
                if self._clusters[candidates[0]].size() >= self._clusters[candidates[1]].size():
                    repulsion_index = candidates[1]
                    stay_index = candidates[0]
                else:
                    repulsion_index = candidates[0]
                    stay_index = candidates[1]

                if self._clusters[repulsion_index].border_left().x >= self._clusters[stay_index].border_right().x:
                    if self._clusters[repulsion_index].status.UP_ALONG_SURFACE:
                        self._clusters[repulsion_index].status = Status.DOWN_ALONG_SURFACE
                else:
                    if self._clusters[repulsion_index].status != Status.UP_ALONG_SURFACE:
                        self._clusters[repulsion_index].status = Status.UP_ALONG_SURFACE

                self.cluster_uncoloring(self._clusters.get(repulsion_index))
                self._clusters[repulsion_index].transition()
                self.cluster_coloring(self._clusters.get(repulsion_index))

    def queue_transit(self):
        """Процедура движения кластеров (имитация в дискретной модели), поднимает кластеры со статусом BREAKING_AWAY
        с поверхности, передвигает кластеры со статусами UP_ALONG_SURFACE, DOWN_ALONG_SURFACE вдоль поверхности"""

        for cluster in self._clusters.values():
            if cluster.status == Status.ON_SURFACE or cluster.status == Status.OFF_SURFACE:
                continue

            if cluster.status == Status.DOWN_ALONG_SURFACE or cluster.status == Status.UP_ALONG_SURFACE:
                speed = cluster.speed()
                if speed >= self._rows:
                    speed -= 1
                _exit = False

                j = speed
                while j > 0 and not _exit:
                    self.check_cluster_for_clusters(cluster.number)
                    if cluster.status == Status.MERGING or cluster.status == Status.ON_SURFACE:
                        _exit = True
                        continue
                    self.cluster_uncoloring(self._clusters.get(cluster.number))
                    cluster.transition()
                    self.cluster_coloring(self._clusters.get(cluster.number))
                    j -= 1

            if cluster.status == Status.BREAKING_AWAY:
                if cluster.can_separating():
                    self.check_cluster_for_clusters(cluster.number)
                    if cluster.status == Status.MERGING or cluster.status == Status.ON_SURFACE:
                        continue
                    self.cluster_uncoloring(self._clusters.get(cluster.number))
                    cluster.separation()
                    self.cluster_coloring(self._clusters.get(cluster.number))
                elif cluster.border_left().y != 0:
                    cluster.status = random.choice((Status.UP_ALONG_SURFACE, Status.DOWN_ALONG_SURFACE))

    def run(self) -> None:
        """Метод, который выполняет один шаг моделирования"""

        create_atom_prob = self._create_atom
        if self._current_mode == Modes.VAR:
            create_atom_prob = random.random()

        rand_create = random.random()
        if rand_create <= create_atom_prob:
            self._atoms_count += 1
            position = random.randint(0, self._rows - 1)
            current = self.add_atom(position)
            self.create_cluster(current)
            if self._place[current.x][current.y] == 0:
                rand_transition = random.random()
                if rand_transition <= self._transit_atom:
                    current = self.atom_transition(current)                                                     # TODO: можно изменить логику, проверять наличие кластера только для кластеров при отсоединении
                    self.create_cluster(current)                                                                #  а атомы присоединять сразу
            if self._place[current.x][current.y] > 0:
                rand_separation = random.random()
                cluster_number = self._place[current.x][current.y]
                separation_prob = 1.0 - self._clusters[cluster_number].adjoined / self._clusters[cluster_number].size()
                if rand_separation < separation_prob:
                    self._clusters.get(self._place[current.x][current.y]).status = Status.BREAKING_AWAY
            self.queue_transit()  # TODO: добавить проверку на необходимость запуска, как вариант сделать счетчики на каждый тип кластера запускать queue только, когда это требуется

    def draw(self, dr: Drawer) -> None:
        """Метод отрисовки текущей сетки с помощью объекта типа Drawer"""

        for row in range(self._rows):
            for col in range(self._columns):
                if self._place[row][col] != -1:
                    dr.draw_point(row, col, self._place[row][col])

    def create_bar(self) -> dict:
        """Создает гистограмму полученных результатов моделирования"""

        bar = {}
        for cluster in self._clusters.values():
            bar[cluster.size()] = bar.get(cluster.size()) + 1 if bar.get(cluster.size()) else 1
        return bar

    def conclusion_dict(self) -> dict:
        """Возвращает статистику пройденного моделирования"""

        sizes = [cluster.size() for cluster in self._clusters.values()] if len(self._clusters) > 0 else [0]

        avg = statistics.mean(sizes)
        med = statistics.median(sizes)
        span = sizes[-1] - sizes[0]

        return {
            'atoms': self._atoms_count,
            'avg': avg,
            'med': med,
            'span': span,
            'clusters_count': len(self._clusters)
        }  # TODO: сделать валидируюший класс?

    def clusters_conclusion(self, _time: str = None) -> None:
        """Создает для каждого кластера, полученного в результате моделирования, файл с его описанием"""

        for cluster in self._clusters.values():
            if cluster.status == Status.MERGING:
                continue

            cluster_info = f'Номер кластера: {cluster.number}\n' \
                           f'Размер кластера: {cluster.size()}\n' \
                           f'Границы кластера: ' \
                           f'по вертикали: {cluster.border_right().x}, {cluster.border_left().x}; ' \
                           f'по горизонтали: {cluster.border_right().y}, {cluster.border_left().y}\n' \
                           f'Статус: {status_definition.get(cluster.status)}\n\n' \
                           f'Изображение кластера:\n\n'
            cluster_info += cluster.image()

            path = f'results\\ClusterN-{cluster.number}-{_time}.txt'
            with open(path, 'w') as file:
                file.write(cluster_info)
