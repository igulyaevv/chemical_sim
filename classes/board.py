from . import Cell
from . import Cluster

import random

from .Drawer import Drawer
from .Drawable import Drawable

random.seed()


class Board(Drawable):
    def __init__(self, rows: int, addprob: float, transitprob: float, mergeprob: float, mode: int = 0):
        self.rows = rows
        self.columns = 3
        self.place = [[-1] * self.columns for _ in range(self.rows)]
        self.clusters = {}
        self.mode = mode
        self.createAtom = addprob
        self.transitAtom = transitprob
        self.mergeCluster = mergeprob
        self.queue = []
        self.atoms = 0

    def Resize(self) -> None:
        for item in self.place:
            item += [-1] * 3
        self.columns += 3

    def Rows(self) -> int:
        return self.rows

    def AddAtom(self, row: int) -> Cell:
        j = 0
        if self.place[row][0] == -1:
            self.place[row][0] = 0
        else:
            while self.place[row][j] != -1:                                                                 # выкидывает ошибку
                if j >= self.columns:
                    self.Resize()
                    break
                j += 1
            self.place[row][j] = 0
        return Cell(row, j)

    def CheckCluster(self, current: Cell, candidates: list, tempPlace: list) -> None:
        x = current.x
        y = current.y
        cur_val = self.place[x][y] if 0 <= x < self.rows and 0 <= y < self.columns else -2
        if x - 1 >= 0 and x + 1 < self.rows and y - 1 >= 0 and y + 1 < self.columns and \
                self.place[x - 1][y] == cur_val and self.place[x + 1][y] == cur_val and \
                self.place[x][y - 1] == cur_val and self.place[x][y + 1] == cur_val and \
                self.place[x + 1][y + 1] == cur_val and self.place[x - 1][y + 1] == cur_val and \
                self.place[x + 1][y - 1] == cur_val and self.place[x - 1][y - 1] == cur_val:
            return
        if 0 <= x < self.rows and 0 <= y < self.columns and self.place[x][y] != -1 and tempPlace[x][y] != 1:
            tempPlace[x][y] = 1
            candidates.append(Cell(x, y))

            self.CheckCluster(Cell(x - 1, y), candidates, tempPlace)
            self.CheckCluster(Cell(x + 1, y), candidates, tempPlace)
            self.CheckCluster(Cell(x, y - 1), candidates, tempPlace)
            self.CheckCluster(Cell(x, y + 1), candidates, tempPlace)
            self.CheckCluster(Cell(x + 1, y + 1), candidates, tempPlace)
            self.CheckCluster(Cell(x + 1, y - 1), candidates, tempPlace)
            self.CheckCluster(Cell(x - 1, y + 1), candidates, tempPlace)
            self.CheckCluster(Cell(x - 1, y - 1), candidates, tempPlace)

    def CreateCluster(self, current: Cell) -> None:
        tempPlace = [[0] * self.columns for _ in range(self.rows)]
        candidates = []
        self.CheckCluster(current, candidates, tempPlace)

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
                    new_cluster.Add_Atom(item)
                self.clusters[new_cluster.Number()] = new_cluster
                self.ClusterColoring(self.clusters.get(new_cluster.Number()))
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
                        self.clusters[new_found].Add_Atom(item)
                        self.ClusterColoring(self.clusters.get(new_found))
            if len(merging) > 0:
                self.ClusterMerger([i for i in merging] + [min_clusternumber])

    def AtomTransition(self, current: Cell) -> Cell:
        rand = random.random()
        isUp = True
        if rand > 0.5:
            isUp = False

        if isUp and current.x - 1 >= 0:
            self.place[current.x][current.y] = -1
            current = self.AddAtom(current.x - 1)
        elif not isUp and current.x + 1 < self.rows:
            self.place[current.x][current.y] = -1
            current = self.AddAtom(current.x + 1)
        return current

    def CheckClusterforClusters(self, found: int) -> None:
        clusterNumber = self.clusters[found].Number()
        for i in range(self.clusters[found].Size()):
            x = self.clusters[found].Atoms()[i].x
            y = self.clusters[found].Atoms()[i].y
            if 0 <= x < self.rows and 0 <= y < self.columns:
                if (x - 1 >= 0 and self.place[x - 1][y] != clusterNumber and self.place[x - 1][y] != -1 or
                        x + 1 < self.rows and self.place[x + 1][y] != clusterNumber and self.place[x + 1][y] != -1 or
                        y - 1 >= 0 and self.place[x][y - 1] != clusterNumber and self.place[x][y - 1] != -1 or
                        y + 1 < self.columns and self.place[x][y + 1] != clusterNumber and self.place[x][y + 1] != -1 or
                        x - 1 >= 0 and y - 1 >= 0 and self.place[x - 1][y - 1] != clusterNumber and self.place[x - 1][
                            y - 1] != -1 or
                        x - 1 >= 0 and y + 1 < self.columns and self.place[x - 1][y + 1] != clusterNumber and
                        self.place[x - 1][y + 1] != -1 or
                        x + 1 < self.rows and y - 1 >= 0 and self.place[x + 1][y - 1] != clusterNumber and
                        self.place[x + 1][y - 1] != -1 or
                        x + 1 < self.rows and y + 1 < self.columns and self.place[x + 1][y + 1] != clusterNumber and
                        self.place[x + 1][y + 1] != -1):
                    self.CreateCluster(self.clusters[found].Atoms()[i])
                    return

    def ClusterUncoloring(self, cluster: Cluster) -> None:
        for item in cluster.Atoms():
            if 0 <= item.x < self.rows and 0 <= item.y < self.columns:
                self.place[item.x][item.y] = -1

    def ClusterColoring(self, cluster: Cluster) -> None:
        for item in cluster.Atoms():
            if item.y >= self.columns:
                self.Resize()
            if 0 <= item.x < self.rows and 0 <= item.y < self.columns:
                self.place[item.x][item.y] = cluster.Number()

    def ClusterMerger(self, candidates: list) -> None:
        if len(candidates) > 2:
            for i in range(len(candidates) - 1):
                self.clusters[candidates[-1]].Merger(self.clusters[candidates[i]])
                self.clusters[candidates[i]].NotIsMerged()
                self.ClusterUncoloring(self.clusters[candidates[i]])
            self.ClusterColoring(self.clusters.get(candidates[-1]))
        else:
            randmerge = random.random()
            if randmerge <= self.mergeCluster or self.clusters[candidates[0]].IsOnTheSurface() or \
                    self.clusters[candidates[1]].IsOnTheSurface() or True:                                         # временное решение
                self.clusters[candidates[1]].Merger(self.clusters[candidates[0]])                                  # подумать над этой проблемой (сделать доп. проверку на повторяющиеся ячейки в Merger ?)
                self.ClusterUncoloring(self.clusters[candidates[0]])
                self.ClusterColoring(self.clusters[candidates[1]])
                self.clusters[candidates[0]].NotIsMerged()
            else:
                if self.clusters[candidates[0]].Size() >= self.clusters[candidates[1]].Size():
                    repulsion_index = candidates[1]
                    stay_index = candidates[0]
                else:
                    repulsion_index = candidates[0]
                    stay_index = candidates[1]

                if self.clusters[repulsion_index].Min().x >= self.clusters[stay_index].Max().x:
                    if self.clusters[repulsion_index].IsUp():                                                    # тут скорее всего ошибка, нужно переработать всю механику
                        self.clusters[repulsion_index].ChangeWay()
                else:
                    if not self.clusters[repulsion_index].IsUp():
                        self.clusters[repulsion_index].ChangeWay()

                self.ClusterUncoloring(self.clusters.get(repulsion_index))
                self.clusters[repulsion_index].Transition(1, self.rows)
                self.ClusterColoring(self.clusters.get(repulsion_index))

    def QueueTransit(self) -> None:
        i = 0
        while i < len(self.queue):
            clusterNumber = self.queue[i].x
            if clusterNumber == -1 or self.clusters[clusterNumber].IsDeleted() or self.clusters[clusterNumber].IsMerged():
                del self.queue[i]
                continue
            else:
                if self.queue[i].y > 0:
                    self.queue[i].y -= 1
                    self.CheckClusterforClusters(clusterNumber)
                    if self.clusters[clusterNumber].IsMerged():
                        del self.queue[i]
                        continue
                    self.ClusterUncoloring(self.clusters.get(clusterNumber))
                    self.clusters[clusterNumber].Separation(1)
                    self.ClusterColoring(self.clusters.get(clusterNumber))
                else:
                    rand = random.randint(0, 32767) % self.clusters[clusterNumber].Size()
                    V = self.clusters[clusterNumber].Size() if 1 + rand > self.clusters[clusterNumber].Size() else 1 + rand
                    if V >= self.rows:
                        V = self.rows - 1
                    _exit = False

                    j = V
                    while j > 0 and not _exit:
                        self.CheckClusterforClusters(clusterNumber)
                        if self.clusters[clusterNumber].IsMerged() or self.clusters[clusterNumber].IsOnTheSurface():
                            del self.queue[i]
                            _exit = True
                            continue
                        self.ClusterUncoloring(self.clusters.get(clusterNumber))
                        self.clusters[clusterNumber].Transition(1, self.rows)
                        self.ClusterColoring(self.clusters.get(clusterNumber))
                        j -= 1
            i += 1

    def Run(self) -> None:
        createAtomProb = self.createAtom
        if self.mode == 1:
            createAtomProb = 0.001 * (random.randint(0, 32767) % int(self.createAtom * 1001))

        randcreate = random.random()
        if randcreate <= createAtomProb:
            self.atoms += 1
            position = random.randint(0, 32767) % self.rows
            current = self.AddAtom(position)
            self.CreateCluster(current)
            # self.Render()
            # time.sleep(1)
            if self.place[current.x][current.y] == 0:
                randtransition = random.random()
                if randtransition <= self.transitAtom:
                    current = self.AtomTransition(current)                                                     # можно изменить логику, проверять наличие кластера только для кластеров при отсоединении
                    self.CreateCluster(current)                                                                # а атомы присоединять сразу
                    # self.Render()
                    # time.sleep(1)
            if self.place[current.x][current.y] > 0:
                randseparation = random.random()
                clusterNumber = self.place[current.x][current.y]
                separationprob = 1.0 - float(self.clusters[clusterNumber].Adjoined()) / float(self.clusters[clusterNumber].Size())
                if randseparation < separationprob:
                    sep = self.clusters[clusterNumber].Size() / 2 if self.clusters[clusterNumber].Size() / 2 < self.rows else self.rows - 1
                    new_separation = Cell(self.place[current.x][current.y], sep if sep >= 1 else 1)         # убрать Cell отсюда и добавить читаемые статусы
                    self.queue.append(new_separation)
            if len(self.queue) != 0:
                self.QueueTransit()
            # self.Render()
            # time.sleep(1)

    def Render(self) -> None:
        for i in range(self.rows):
            for j in range(self.columns):
                if self.place[i][j] == -1:
                    print(' ', end='')
                else:
                    # print('*', end='')
                    print(self.place[i][j], end='')
            print()
        print('----------')

    def draw(self, dr: Drawer) -> None:
        for i in range(self.rows):
            for j in range(self.columns):
                if self.place[i][j] != -1:
                    dr.draw_point(i, j, self.place[i][j])

    def create_bar(self) -> dict:
        d = {}
        for value in self.clusters.values():
            d[value.Size()] = d.get(value.Size()) + 1 if d.get(value.Size()) else 1
        return d

    def conclusion_dict(self) -> dict:
        avg = 0
        for value in self.clusters.values():
            if value.IsMerged():
                continue
            avg += value.Size()

        notinCluster = 0
        for t in range(self.rows):
            for k in range(self.columns):
                if self.place[t][k] == 0:
                    notinCluster += 1

        return {'atoms': self.atoms,
                'loss': self.atoms - avg - notinCluster,
                'avg': avg / len(self.clusters) if len(self.clusters) != 0 else 0,
                'med': 0, # (self.clusters[int(len(self.clusters) / 2)].Size() if len(self.clusters) % 2 == 0 or len(self.clusters) == 1 or len(self.clusters) == 0 else (self.clusters[int(len(self.clusters) / 2)].Size() + self.clusters[int(len(self.clusters) / 2) + 1].Size()) / 2) if len(self.clusters) > 0 else 0,
                'span': 0, # self.clusters[len(self.clusters) - 1].Size() - self.clusters[0].Size() if len(self.clusters) > 0 else 0
                'clusters_count': len(self.clusters)
                }

    def clusters_conclusion(self, _time: str = None) -> None:
        for value in self.clusters.values():
            if value.IsMerged():
                continue

            clusterinfo = f'Номер кластера: {value.Number()}\nРазмер кластера (количество атомов): {value.Size()}\n' \
                          f'Крайние точки кластера: по вертикали: {value.Max().x}, {value.Min().x}; ' \
                          f'по горизонтали: {value.Max().y}, {value.Min().y}\nСтатус:'
            if value.IsOnTheSurface():
                clusterinfo += 'На поверхности\n\n'
            elif not value.IsDeleted():
                clusterinfo += 'Вне поверхности, в пределах области видимости\n\n'
            else:
                clusterinfo += 'Вне пределов области видимости\n\n'

            clusterinfo += 'Отрисовка кластера:\n\n'
            for t in range(value.Max().x - value.Min().x + 1):
                for j in range(value.Max().y - value.Min().y + 1):
                    for k in range(value.Size()):
                        if value.Atoms()[k].x - value.Min().x == t and value.Atoms()[k].y - value.Min().y == j:
                            clusterinfo += '*'
                            break
                        if k == value.Size() - 1:
                            clusterinfo += ' '
                clusterinfo += '\n'
                path = f'results\\ClusterN-{value.Number()}-{_time}.txt'
                with open(path, 'w') as file:
                    file.write(clusterinfo)
