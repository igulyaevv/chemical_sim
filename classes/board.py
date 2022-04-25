from . import Cell
from . import Cluster

import random

from interfaces.Drawer import Drawer
from interfaces.Drawable import Drawable

from resources.constants import RESIZE, Status

random.seed()


class Board(Drawable):
    def __init__(self, rows: int, addprob: float, transitprob: float, mergeprob: float, mode: int = 0):
        self.rows = rows
        self.columns = RESIZE
        self.place = [[-1] * self.columns for _ in range(self.rows)]
        self.clusters = {}
        self.mode = mode
        self.createAtom = addprob
        self.transitAtom = transitprob
        self.mergeCluster = mergeprob
        self.queue = []
        self.atoms = 0

    def resize(self) -> None:
        for item in self.place:
            item += [-1] * RESIZE
        self.columns += RESIZE

    def add_atom(self, row: int) -> Cell:
        j = self.place[row].index(-1) if -1 in self.place[row] else self.columns
        if j >= self.columns:
            self.resize()
            j += RESIZE
        self.place[row][j] = 0

        return Cell(row, j)

    def check_cluster(self, current: Cell, candidates: list, temp_place: list) -> None:
        x = current.x
        y = current.y
        cur_val = self.place[x][y] if 0 <= x < self.rows and 0 <= y < self.columns else -2
        if x - 1 >= 0 and x + 1 < self.rows and y - 1 >= 0 and y + 1 < self.columns and \
                self.place[x - 1][y] == cur_val and self.place[x + 1][y] == cur_val and \
                self.place[x][y - 1] == cur_val and self.place[x][y + 1] == cur_val and \
                self.place[x + 1][y + 1] == cur_val and self.place[x - 1][y + 1] == cur_val and \
                self.place[x + 1][y - 1] == cur_val and self.place[x - 1][y - 1] == cur_val:
            return
        if 0 <= x < self.rows and 0 <= y < self.columns and self.place[x][y] != -1 and temp_place[x][y] != 1:
            temp_place[x][y] = 1
            candidates.append(Cell(x, y))

            self.check_cluster(Cell(x - 1, y), candidates, temp_place)
            self.check_cluster(Cell(x + 1, y), candidates, temp_place)
            self.check_cluster(Cell(x, y - 1), candidates, temp_place)
            self.check_cluster(Cell(x, y + 1), candidates, temp_place)
            self.check_cluster(Cell(x + 1, y + 1), candidates, temp_place)
            self.check_cluster(Cell(x + 1, y - 1), candidates, temp_place)
            self.check_cluster(Cell(x - 1, y + 1), candidates, temp_place)
            self.check_cluster(Cell(x - 1, y - 1), candidates, temp_place)

    def create_cluster(self, current: Cell) -> None:
        temp_place = [[0] * self.columns for _ in range(self.rows)]
        candidates = []
        self.check_cluster(current, candidates, temp_place)

        min_clusternumber = 0
        for item in candidates:
            if self.place[item.x][item.y] != 0:
                if min_clusternumber == 0:
                    min_clusternumber = self.place[item.x][item.y]
                elif self.place[item.x][item.y] < min_clusternumber:
                    min_clusternumber = self.place[item.x][item.y]

        if min_clusternumber == 0:
            if len(candidates) >= 4:
                new_cluster = Cluster()
                for item in candidates:
                    new_cluster.add_atom(item)
                self.clusters[new_cluster.number()] = new_cluster
                self.cluster_coloring(self.clusters.get(new_cluster.number()))
        else:
            merging = set()
            for item in candidates:
                if self.place[item.x][item.y] == min_clusternumber:
                    continue
                elif self.place[item.x][item.y] != 0:
                    merging.add(self.place[item.x][item.y])
                else:
                    new_found = -1
                    if item.x - 1 >= 0 and self.place[item.x - 1][item.y] > 0:
                        new_found = self.place[item.x - 1][item.y]

                    if item.x + 1 < self.rows and self.place[item.x + 1][item.y] > 0:
                        new_found = self.place[item.x + 1][item.y]

                    if item.y - 1 >= 0 and self.place[item.x][item.y - 1] > 0:
                        new_found = self.place[item.x][item.y - 1]

                    if item.y + 1 < self.columns and self.place[item.x][item.y + 1] > 0:
                        new_found = self.place[item.x][item.y + 1]

                    if item.x - 1 >= 0 and item.y - 1 >= 0 and self.place[item.x - 1][item.y - 1] > 0:
                        new_found = self.place[item.x - 1][item.y - 1]

                    if item.x - 1 >= 0 and item.y + 1 < self.columns and self.place[item.x - 1][item.y + 1] > 0:
                        new_found = self.place[item.x - 1][item.y + 1]

                    if item.x + 1 < self.rows and item.y - 1 >= 0 and self.place[item.x + 1][item.y - 1] > 0:
                        new_found = self.place[item.x + 1][item.y - 1]

                    if item.x + 1 < self.rows and item.y + 1 < self.columns and self.place[item.x + 1][item.y + 1] > 0:
                        new_found = self.place[item.x + 1][item.y + 1]

                    if new_found != -1:
                        self.clusters[new_found].add_atom(item)
                        self.cluster_coloring(self.clusters.get(new_found))
            if len(merging) > 0:
                self.cluster_merger([i for i in merging] + [min_clusternumber])

    def atom_transition(self, current: Cell) -> Cell:
        rand = random.choice((True, False))
        is_up = True if rand else False

        self.place[current.x][current.y] = -1

        if is_up and current.x - 1 >= 0:
            current = self.add_atom(current.x - 1)
        elif not is_up and current.x + 1 < self.rows:
            current = self.add_atom(current.x + 1)

        return current

    def check_cluster_for_clusters(self, found: int) -> None:
        cluster_number = self.clusters[found].number()
        for i in range(self.clusters[found].size()):
            x = self.clusters[found].Atoms()[i].x
            y = self.clusters[found].Atoms()[i].y
            if 0 <= x < self.rows and 0 <= y < self.columns:
                if (x - 1 >= 0 and self.place[x - 1][y] != cluster_number and self.place[x - 1][y] != -1 or
                        x + 1 < self.rows and self.place[x + 1][y] != cluster_number and self.place[x + 1][y] != -1 or
                        y - 1 >= 0 and self.place[x][y - 1] != cluster_number and self.place[x][y - 1] != -1 or
                        y + 1 < self.columns and self.place[x][y + 1] != cluster_number and self.place[x][y + 1] != -1 or
                        x - 1 >= 0 and y - 1 >= 0 and self.place[x - 1][y - 1] != cluster_number and self.place[x - 1][
                            y - 1] != -1 or
                        x - 1 >= 0 and y + 1 < self.columns and self.place[x - 1][y + 1] != cluster_number and
                        self.place[x - 1][y + 1] != -1 or
                        x + 1 < self.rows and y - 1 >= 0 and self.place[x + 1][y - 1] != cluster_number and
                        self.place[x + 1][y - 1] != -1 or
                        x + 1 < self.rows and y + 1 < self.columns and self.place[x + 1][y + 1] != cluster_number and
                        self.place[x + 1][y + 1] != -1):
                    self.create_cluster(self.clusters[found].Atoms()[i])
                    return

    def cluster_uncoloring(self, cluster: Cluster) -> None:
        for item in cluster.Atoms():
            if 0 <= item.x < self.rows and 0 <= item.y < self.columns:
                self.place[item.x][item.y] = -1

    def cluster_coloring(self, cluster: Cluster) -> None:
        for item in cluster.Atoms():
            if item.y >= self.columns:
                self.resize()
            if 0 <= item.x < self.rows and 0 <= item.y < self.columns:
                self.place[item.x][item.y] = cluster.number()

    def cluster_merger(self, candidates: list) -> None:
        if len(candidates) > 2:
            for i in range(len(candidates) - 1):
                self.clusters[candidates[-1]].merger(self.clusters[candidates[i]])
                self.clusters[candidates[i]].NotIsMerged()
                self.cluster_uncoloring(self.clusters[candidates[i]])
            self.cluster_coloring(self.clusters.get(candidates[-1]))
        else:
            randmerge = random.random()
            if randmerge <= self.mergeCluster or self.clusters[candidates[0]].IsOnTheSurface() or \
                    self.clusters[candidates[1]].IsOnTheSurface() or True:                                         # TODO: временное решение
                self.clusters[candidates[1]].merger(self.clusters[candidates[0]])                                  # TODO: подумать над этой проблемой (сделать доп. проверку на повторяющиеся ячейки в merger ?)
                self.cluster_uncoloring(self.clusters[candidates[0]])
                self.cluster_coloring(self.clusters[candidates[1]])
                self.clusters[candidates[0]].NotIsMerged()
            else:
                if self.clusters[candidates[0]].size() >= self.clusters[candidates[1]].size():
                    repulsion_index = candidates[1]
                    stay_index = candidates[0]
                else:
                    repulsion_index = candidates[0]
                    stay_index = candidates[1]

                if self.clusters[repulsion_index].border_left().x >= self.clusters[stay_index].border_right().x:
                    if self.clusters[repulsion_index].is_up():                                                    # TODO: тут скорее всего ошибка, нужно переработать всю механику
                        self.clusters[repulsion_index].change_way()
                else:
                    if not self.clusters[repulsion_index].is_up():
                        self.clusters[repulsion_index].change_way()

                self.cluster_uncoloring(self.clusters.get(repulsion_index))
                self.clusters[repulsion_index].transition(1, self.rows)
                self.cluster_coloring(self.clusters.get(repulsion_index))

    def queue_transit(self) -> None:
        i = 0
        while i < len(self.queue):
            cluster_number = self.queue[i].x
            if cluster_number == -1 or self.clusters[cluster_number].IsDeleted() or self.clusters[cluster_number].IsMerged():
                del self.queue[i]
                continue
            else:
                if self.queue[i].y > 0:
                    self.queue[i].y -= 1
                    self.check_cluster_for_clusters(cluster_number)
                    if self.clusters[cluster_number].IsMerged():
                        del self.queue[i]
                        continue
                    self.cluster_uncoloring(self.clusters.get(cluster_number))
                    self.clusters[cluster_number].separation(1)
                    self.cluster_coloring(self.clusters.get(cluster_number))
                else:
                    rand = random.randint(0, self.clusters[cluster_number].size() - 1)
                    V = self.clusters[cluster_number].size() if 1 + rand > self.clusters[cluster_number].size() else 1 + rand
                    if V >= self.rows:
                        V = self.rows - 1
                    _exit = False

                    j = V
                    while j > 0 and not _exit:
                        self.check_cluster_for_clusters(cluster_number)
                        if self.clusters[cluster_number].IsMerged() or self.clusters[cluster_number].IsOnTheSurface():
                            del self.queue[i]
                            _exit = True
                            continue
                        self.cluster_uncoloring(self.clusters.get(cluster_number))
                        self.clusters[cluster_number].transition(1, self.rows)
                        self.cluster_coloring(self.clusters.get(cluster_number))
                        j -= 1
            i += 1

    def run(self) -> None:
        create_atom_prob = self.createAtom
        if self.mode == 1:
            create_atom_prob = random.random()

        randcreate = random.random()
        if randcreate <= create_atom_prob:
            self.atoms += 1
            position = random.randint(0, self.rows - 1)
            current = self.add_atom(position)
            self.create_cluster(current)
            if self.place[current.x][current.y] == 0:
                randtransition = random.random()
                if randtransition <= self.transitAtom:
                    current = self.atom_transition(current)                                                     # TODO: можно изменить логику, проверять наличие кластера только для кластеров при отсоединении
                    self.create_cluster(current)                                                                # а атомы присоединять сразу
            if self.place[current.x][current.y] > 0:
                randseparation = random.random()
                clusterNumber = self.place[current.x][current.y]
                separationprob = 1.0 - float(self.clusters[clusterNumber].adjoined()) / float(self.clusters[clusterNumber].size())
                if randseparation < separationprob:
                    sep = self.clusters[clusterNumber].size() / 2 if self.clusters[clusterNumber].size() / 2 < self.rows else self.rows - 1
                    new_separation = Cell(self.place[current.x][current.y], sep if sep >= 1 else 1)         # TODO: убрать Cell отсюда и добавить читаемые статусы
                    self.queue.append(new_separation)
            if len(self.queue) != 0:
                self.queue_transit()

    def draw(self, dr: Drawer) -> None:
        for i in range(self.rows):
            for j in range(self.columns):
                if self.place[i][j] != -1:
                    dr.draw_point(i, j, self.place[i][j])

    def create_bar(self) -> dict:
        d = {}
        for value in self.clusters.values():
            d[value.size()] = d.get(value.size()) + 1 if d.get(value.size()) else 1
        return d

    def conclusion_dict(self) -> dict:
        avg = sum((value.size() if value.IsMerged() else 0 for value in self.clusters.values()))
        not_in_cluster = sum((1 if self.place[i][j] == 0 else 0 for i in range(self.rows) for j in range(self.columns)))

        lengths = [i.size() for i in self.clusters.values()]
        lengths.sort()

        return {
            'atoms': self.atoms,
            'loss': 0,  # self.atoms - avg - not_in_cluster,
            'avg': avg / len(self.clusters) if len(self.clusters) != 0 else 0,
            'med': (lengths[int(len(lengths) / 2)] if len(lengths) % 2 == 0 or len(lengths) == 1 or len(lengths) == 0 else (lengths[int(len(lengths) / 2)] + lengths[int(len(lengths) / 2) + 1]) / 2) if len(lengths) > 0 else 0,
            'span': lengths[-1] - lengths[0] if len(lengths) > 0 else 0,
            'clusters_count': len(self.clusters)
        }

    def clusters_conclusion(self, _time: str = None) -> None:
        for value in self.clusters.values():
            if value.IsMerged():
                continue

            clusterinfo = f'Номер кластера: {value.number()}\nРазмер кластера (количество атомов): {value.size()}\n' \
                          f'Крайние точки кластера: по вертикали: {value.border_right().x}, {value.border_left().x}; ' \
                          f'по горизонтали: {value.border_right().y}, {value.border_left().y}\nСтатус:'
            if value.IsOnTheSurface():
                clusterinfo += 'На поверхности\n\n'
            elif not value.IsDeleted():
                clusterinfo += 'Вне поверхности, в пределах области видимости\n\n'
            else:
                clusterinfo += 'Вне пределов области видимости\n\n'

            clusterinfo += 'Отрисовка кластера:\n\n'
            for t in range(value.border_right().x - value.border_left().x + 1):
                for j in range(value.border_right().y - value.border_left().y + 1):
                    for k in range(value.size()):
                        if value.Atoms()[k].x - value.border_left().x == t and value.Atoms()[k].y - value.border_left().y == j:
                            clusterinfo += '*'
                            break
                        if k == value.size() - 1:
                            clusterinfo += ' '
                clusterinfo += '\n'
                path = f'results\\ClusterN-{value.number()}-{_time}.txt'
                with open(path, 'w') as file:
                    file.write(clusterinfo)
