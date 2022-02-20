from . import Cell
from . import Cluster

import random

from .Drawer import Drawer
from .Drawable import Drawable


class Board(Drawable):
    def __init__(self, rows: int, addprob: float, transitprob: float, mergeprob: float, mode: int = 0):
        self.rows = rows
        self.columns = 3
        self.place = [[-1] * self.columns for _ in range(self.rows)]
        self.clusters = []
        self.mode = mode
        self.createAtom = addprob
        self.transitAtom = transitprob
        self.mergeCluster = mergeprob
        self.queue = []
        self.atoms = 0

    def Resize(self) -> None:
        for i in range(len(self.place)):
            self.place[i] = self.place[i] + [-1] * 3
        self.columns += 3

    def Rows(self) -> int:
        return self.rows

    def AddAtom(self, row: int) -> Cell:
        j = 0
        if self.place[row][0] == -1:
            self.place[row][0] = 0
        else:
            while self.place[row][j] != -1 and j < self.columns:
                j += 1
            if j >= self.columns:
                self.Resize()
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
        if 0 <= current.x < self.rows and 0 <= current.y < self.columns and self.place[current.x][current.y] != -1 \
                and tempPlace[current.x][current.y] != 1:
            candidate = Cell(current.x, current.y)
            tempPlace[current.x][current.y] = 1
            candidates.append(candidate)

            self.CheckCluster(Cell(current.x - 1, current.y), candidates, tempPlace)
            self.CheckCluster(Cell(current.x + 1, current.y), candidates, tempPlace)
            self.CheckCluster(Cell(current.x, current.y - 1), candidates, tempPlace)
            self.CheckCluster(Cell(current.x, current.y + 1), candidates, tempPlace)
            self.CheckCluster(Cell(current.x + 1, current.y + 1), candidates, tempPlace)
            self.CheckCluster(Cell(current.x + 1, current.y - 1), candidates, tempPlace)
            self.CheckCluster(Cell(current.x - 1, current.y + 1), candidates, tempPlace)
            self.CheckCluster(Cell(current.x - 1, current.y - 1), candidates, tempPlace)

    def CreateCluster(self, current: Cell) -> None:
        min_clusternumber = 0
        tempPlace = [[0] * self.columns for _ in range(self.rows)]
        candidates = []
        self.CheckCluster(current, candidates, tempPlace)
        count = len(candidates)

        for i in range(count):
            if self.place[candidates[i].x][candidates[i].y] != 0:
                if min_clusternumber == 0:
                    min_clusternumber = self.place[candidates[i].x][candidates[i].y]
                elif self.place[candidates[i].x][candidates[i].y] < min_clusternumber:
                    min_clusternumber = self.place[candidates[i].x][candidates[i].y]

        if min_clusternumber == 0:
            if count >= 4:
                new_cluster = Cluster()
                for i in range(count):
                    new_cluster.Add_Atom(candidates[i])
                self.clusters.append(new_cluster)
                found = self.ClusterSearch(new_cluster.Number())
                self.ClusterColoring(found)
        else:
            found = self.ClusterSearch(min_clusternumber)
            merging = set()
            for i in range(count):
                if self.place[candidates[i].x][candidates[i].y] == min_clusternumber:
                    continue
                elif self.place[candidates[i].x][candidates[i].y] != 0:
                    another_found = self.ClusterSearch(self.place[candidates[i].x][candidates[i].y])
                    merging.add(another_found)
                else:
                    new_found = -1
                    if candidates[i].x - 1 >= 0 and self.place[candidates[i].x - 1][candidates[i].y] > 0:
                        new_found = self.ClusterSearch(self.place[candidates[i].x - 1][candidates[i].y])

                    if candidates[i].x + 1 < self.rows and self.place[candidates[i].x + 1][candidates[i].y] > 0:
                        new_found = self.ClusterSearch(self.place[candidates[i].x + 1][candidates[i].y])

                    if candidates[i].y - 1 >= 0 and self.place[candidates[i].x][candidates[i].y - 1] > 0:
                        new_found = self.ClusterSearch(self.place[candidates[i].x][candidates[i].y - 1])

                    if candidates[i].y + 1 < self.columns and self.place[candidates[i].x][candidates[i].y + 1] > 0:
                        new_found = self.ClusterSearch(self.place[candidates[i].x][candidates[i].y + 1])

                    if candidates[i].x - 1 >= 0 and candidates[i].y - 1 >= 0 and self.place[candidates[i].x - 1][
                        candidates[i].y - 1] > 0:
                        new_found = self.ClusterSearch(self.place[candidates[i].x - 1][candidates[i].y - 1])

                    if candidates[i].x - 1 >= 0 and candidates[i].y + 1 < self.columns and \
                            self.place[candidates[i].x - 1][candidates[i].y + 1] > 0:
                        new_found = self.ClusterSearch(self.place[candidates[i].x - 1][candidates[i].y + 1])

                    if candidates[i].x + 1 < self.rows and candidates[i].y - 1 >= 0 and self.place[candidates[i].x + 1][
                        candidates[i].y - 1] > 0:
                        new_found = self.ClusterSearch(self.place[candidates[i].x + 1][candidates[i].y - 1])

                    if candidates[i].x + 1 < self.rows and candidates[i].y + 1 < self.columns and \
                            self.place[candidates[i].x + 1][candidates[i].y + 1] > 0:
                        new_found = self.ClusterSearch(self.place[candidates[i].x + 1][candidates[i].y + 1])
                    if new_found != -1:
                        self.clusters[new_found].Add_Atom(candidates[i])
                        self.ClusterColoring(new_found)
            if len(merging) > 0:
                self.ClusterMerger([i for i in merging] + [found])

    def AtomTransition(self, current: Cell) -> Cell:
        random.seed()

        randway = 0.001 * (random.randint(0, 32767) % 1001)
        UporDown = True
        if randway > 0.5:
            UporDown = False

        if UporDown and current.x - 1 >= 0:
            self.place[current.x][current.y] = -1
            current = self.AddAtom(current.x - 1)
        elif not UporDown and current.x + 1 < self.rows:
            self.place[current.x][current.y] = -1
            current = self.AddAtom(current.x + 1)
        return current

    def ClusterSearch(self, number: int) -> int:
        found = -1
        for i in range(len(self.clusters)):
            if self.clusters[i].Number() == number:
                found = i
        return found

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

    def ClusterUncoloring(self, found: int) -> None:
        for i in range(len(self.clusters[found].Atoms())):
            if (0 <= self.clusters[found].Atoms()[i].x < self.rows and
                    0 <= self.clusters[found].Atoms()[i].y < self.columns):
                self.place[self.clusters[found].Atoms()[i].x][self.clusters[found].Atoms()[i].y] = -1

    def ClusterColoring(self, found: int) -> None:
        for i in range(len(self.clusters[found].Atoms())):
            if self.clusters[found].Atoms()[i].y >= self.columns:
                self.Resize()
            if (0 <= self.clusters[found].Atoms()[i].x < self.rows and
                    0 <= self.clusters[found].Atoms()[i].y < self.columns):
                self.place[self.clusters[found].Atoms()[i].x][self.clusters[found].Atoms()[i].y] = self.clusters[
                    found].Number()

    def ClusterMerger(self, candidates: list) -> None:
        random.seed()

        if len(candidates) > 2:
            for i in range(len(candidates) - 1):
                self.clusters[len(candidates) - 1].Merger(candidates[i], self.clusters)
                self.clusters[candidates[i]].NotIsMerged()
            self.ClusterColoring(len(candidates) - 1)
        else:
            randmerge = 0.001 * (random.randint(0, 32767) % 1001)
            if randmerge <= self.mergeCluster or self.clusters[candidates[0]].IsOnTheSurface() or self.clusters[candidates[1]].IsOnTheSurface():
                self.clusters[candidates[1]].Merger(candidates[0], self.clusters)
                self.clusters[candidates[0]].NotIsMerged()
            else:
                if self.clusters[candidates[0]].Size() >= self.clusters[candidates[1]].Size():
                    repulsion_index = candidates[1]
                    stay_index = candidates[0]
                else:
                    repulsion_index = candidates[0]
                    stay_index = candidates[1]

                if self.clusters[repulsion_index].Min().x >= self.clusters[stay_index].Max().x:
                    if self.clusters[repulsion_index].IsUp():
                        self.clusters[repulsion_index].ChangeWay()
                else:
                    if not self.clusters[repulsion_index].IsUp():
                        self.clusters[repulsion_index].ChangeWay()

                self.ClusterUncoloring(repulsion_index)
                self.clusters[repulsion_index].Transition(1, self.rows)
                self.ClusterColoring(repulsion_index)

    def QueueTransit(self) -> None:
        random.seed()

        i = 0
        while i < len(self.queue):
            found = self.ClusterSearch(self.queue[i].x)
            if found == -1 or self.clusters[found].IsDeleted() or self.clusters[found].IsMerged():
                del self.queue[i]
                continue
            else:
                if self.queue[i].y > 0:
                    self.queue[i].y = self.queue[i].y - 1
                    self.CheckClusterforClusters(found)
                    if self.clusters[found].IsMerged():
                        del self.queue[i]
                        continue
                    self.ClusterUncoloring(found)
                    self.clusters[found].Separation(1)
                    self.ClusterColoring(found)
                else:
                    rand = random.randint(0, 32767) % self.clusters[found].Size()
                    V = self.clusters[found].Size() if 1 + rand > self.clusters[found].Size() else 1 + rand
                    if V >= self.rows:
                        V = self.rows - 1
                    _exit = False

                    j = V
                    while j > 0 and not _exit:
                        self.CheckClusterforClusters(found)
                        if self.clusters[found].IsMerged():
                            del self.queue[i]
                            _exit = True
                            continue
                        self.ClusterUncoloring(found)
                        self.clusters[found].Transition(1, self.rows)
                        self.ClusterColoring(found)
                        j -= 1
            i += 1

    def ClustersSort(self) -> None:
        if len(self.clusters) <= 1:
            return
        for i in range(len(self.clusters) - 1):
            for j in range(len(self.clusters) - i - 1):
                if self.clusters[j].Size() > self.clusters[j + 1].Size():
                    temp = self.clusters[j]
                    self.clusters[j] = self.clusters[j + 1]
                    self.clusters[j + 1] = temp

    def Run(self) -> None:
        random.seed()

        createAtomProb = self.createAtom
        if self.mode == 1:
            createAtomProb = 0.001 * (random.randint(0, 32767) % int(self.createAtom * 1001))

        randcreate = 0.001 * (random.randint(0, 32767) % 1001)
        if randcreate <= createAtomProb:
            self.atoms += 1
            position = random.randint(0, 32767) % self.rows
            current = self.AddAtom(position)
            self.CreateCluster(current)
            # self.Render()
            # time.sleep(1)
            if self.place[current.x][current.y] == 0:
                randtransition = 0.001 * (random.randint(0, 32767) % 1001)
                if randtransition <= self.transitAtom:
                    current = self.AtomTransition(current)
                    self.CreateCluster(current)
                    # self.Render()
                    # time.sleep(1)
            if self.place[current.x][current.y] > 0:
                randseparation = 0.001 * (random.randint(0, 32767) % 1001)
                found = self.ClusterSearch(self.place[current.x][current.y])
                separationprob = 1.0 - float(self.clusters[found].Adjoined()) / float(self.clusters[found].Size())
                if randseparation < separationprob:
                    sep = self.clusters[found].Size() / 2 if self.clusters[found].Size() / 2 <= self.rows else self.rows - 1
                    new_separation = Cell(self.place[current.x][current.y], sep)
                    self.queue.append(new_separation)
            if len(self.queue) != 0:
                self.QueueTransit()
            # self.Render()
            # time.sleep(1)

    def Render(self) -> None:
        for i in range(self.rows):
            for j in range(self.columns):
                if self.place[i][j] == -1:
                    print(' ', '')
                else:
                    # print('*', '')
                    print(self.place[i][j], '')
            print()
        print('----------')

    def draw(self, dr: Drawer) -> None:
        for i in range(self.rows):
            for j in range(self.columns):
                if self.place[i][j] != -1:
                    dr.draw_point(i, j, self.place[i][j])

    def create_bar(self) -> dict:
        d = {}
        for item in self.clusters:
            d[item.Size()] = d.get(item.Size()) + 1 if d.get(item.Size()) else 1
        return d

    def conclusion_dict(self) -> dict:
        self.ClustersSort()
        avg = 0
        for i in range(len(self.clusters)):
            if self.clusters[i].IsMerged():
                continue
            avg += self.clusters[i].Size()

        notinCluster = 0
        for t in range(self.rows):
            for k in range(self.columns):
                if self.place[t][k] == 0:
                    notinCluster += 1

        return {'atoms': self.atoms, 'loss': self.atoms - avg - notinCluster,
                'avg': avg / len(self.clusters) if len(self.clusters) != 0 else 0,
                'med': (self.clusters[int(len(self.clusters) / 2)].Size() if len(self.clusters) % 2 == 0 or len(self.clusters) == 1 or len(self.clusters) == 0 else (self.clusters[int(len(self.clusters) / 2)].Size() + self.clusters[int(len(self.clusters) / 2) + 1].Size()) / 2) if len(self.clusters) > 0 else 0,
                'span': self.clusters[len(self.clusters) - 1].Size() - self.clusters[0].Size() if len(self.clusters) > 0 else 0}

    def Conclusion(self) -> None:
        self.ClustersSort()

        clusterinfo = ''
        distribution = ''
        AverageSize = 0
        print(f'\n---------\nХарактеристика кластеров\nКоличество кластеров: {len(self.clusters)}\n---')
        for i in range(len(self.clusters)):
            if self.clusters[i].IsMerged():
                continue

            print(f'Номер кластера: {self.clusters[i].Number()}\n')
            print(f'Размер кластера (количество атомов): {self.clusters[i].Size()}')
            clusterinfo += 'Вес: ' + str(self.clusters[i].Size()) + '\n'
            print(f'Крайние точки кластера: по вертикали: {self.clusters[i].Max().x}, {self.clusters[i].Min().x}')
            print(f'; по горизонтали: {self.clusters[i].Max().y}, {self.clusters[i].Min().y}')
            if self.clusters[i].IsOnTheSurface():
                temp_str = 'На поверхности'
            elif not self.clusters[i].IsDeleted():
                temp_str = 'Вне поверхности, в пределах области видимости'
            else:
                temp_str = 'Вне пределов области видимости'
            print(f'Статус: {temp_str}\n')
            clusterinfo += temp_str + '\n\n'
            print('Отрисовка кластера')
            for t in range(self.clusters[i].Max().x - self.clusters[i].Min().x + 1):
                for j in range(self.clusters[i].Max().y - self.clusters[i].Min().y + 1):
                    for k in range(self.clusters[i].Size()):
                        if self.clusters[i].Atoms()[k].x - self.clusters[i].Min().x == t and self.clusters[i].Atoms()[k].y - self.clusters[i].Min().y == j:
                            print('*', '')
                            clusterinfo += '*'
                            break
                        if k == self.clusters[i].Size() - 1:
                            print(' ', '')
                            clusterinfo += ' '
                print()
                clusterinfo += '\n'
                path = f'ClusterN-{self.clusters[i].Number()}.txt'
                f = open(path, 'w')
                f.write(clusterinfo)
                f.close()

                distribution += str(self.clusters[i].Size()) + ' '
                print('\n---')
                AverageSize += self.clusters[i].Size()

            print(f'Всего присоединилось атомов: {self.atoms}')
            notinCluster = 0
            for t in range(self.rows):
                for k in range(self.columns):
                    if self.place[t][k] == 0:
                        notinCluster += 1
            print(f'Потеряно атомов: {self.atoms - AverageSize - notinCluster}')

            if len(self.clusters) != 0:
                AverageSize /= len(self.clusters)
            print(f'Медиана веса кластеров: {self.clusters[int(len(self.clusters) / 2)].Size() if len(self.clusters) % 2 == 0 or len(self.clusters) == 1 or len(self.clusters) == 0 else (self.clusters[int(len(self.clusters) / 2)].Size() + self.clusters[int(len(self.clusters) / 2) + 1].Size()) / 2}')

            print(f'\nСреднее значение веса кластеров: {AverageSize}')
            print(f'\nРазмах веса кластеров: {self.clusters[len(self.clusters) - 1].Size() - self.clusters[0].Size()}')

            path = 'WeightAnalysis.txt'
            f = open(path, 'w')
            f.write(distribution)
            f.close()
