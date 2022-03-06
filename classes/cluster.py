import random

from . import Cell

random.seed()


class Cluster:
    IndexCluster = 0

    def __init__(self):
        self.atoms = []
        self.isOnTheSurface = True
        self.isDeleted = False
        self.isUp = True
        randway = random.random()
        if randway > 0.5:
            self.isUp = False
        self.clusterNumber = Cluster.IndexCluster + 1
        Cluster.IndexCluster += 1
        self.adjoined = 0
        self.min = Cell()
        self.max = Cell()

        self.isMerged = False

    def Add_Atom(self, atom: Cell) -> None:
        self.atoms.append(atom)
        self.DefineMinMax()

    def Separation(self, step: int) -> None:
        self.isOnTheSurface = False
        for i in range(step):
            for j in range(len(self.atoms)):
                self.atoms[j].y += 1
        self.DefineMinMax()

    def Transition(self, step: int, rows: int):
        for i in range(step):
            if self.isUp:
                for j in range(len(self.atoms)):
                    self.atoms[j].x += 1 if not self.isUp else -1
                self.DefineMinMax()
                if self.max.x < 0 or self.min.x >= rows:
                    self.isDeleted = True

    def Merger(self, cluster=None) -> None:
        if not cluster:  # or type(cluster) != 'Cluster':
            return
        for item in cluster.Atoms():
            if item in self.atoms:
                continue
            self.Add_Atom(item)
        self.isDeleted = self.isDeleted and cluster.IsDeleted()
        self.isOnTheSurface = self.isOnTheSurface or cluster.IsOnTheSurface()

    def Size(self) -> int:
        return len(self.atoms)

    def Number(self) -> int:
        return self.clusterNumber

    def IsOnTheSurface(self) -> bool:
        return self.isOnTheSurface

    def IsDeleted(self) -> bool:
        return self.isDeleted

    def IsUp(self) -> bool:
        return self.isUp

    def ChangeWay(self) -> None:
        self.isUp = not self.isUp

    def DefineMinMax(self) -> None:
        x_min = self.atoms[0].x
        x_max = self.atoms[0].x
        y_min = self.atoms[0].y
        y_max = self.atoms[0].y
        temp = 0

        for i in range(len(self.atoms)):
            if self.atoms[i].x < x_min:
                x_min = self.atoms[i].x
            if self.atoms[i].x > x_max:
                x_max = self.atoms[i].x

            if self.atoms[i].y < y_min:
                y_min = self.atoms[i].y
            if self.atoms[i].y > y_max:
                y_max = self.atoms[i].y

            if self.atoms[i].y == 0:
                temp += 1

        self.adjoined = temp
        self.max.x = x_max
        self.max.y = y_max
        self.min.x = x_min
        self.min.y = y_min

        if y_min != 0:
            self.isOnTheSurface = False
        else:
            self.isOnTheSurface = True

    def Adjoined(self) -> int:
        return self.adjoined

    def Atoms(self) -> list:
        return self.atoms

    def Max(self) -> Cell:
        return self.max

    def Min(self) -> Cell:
        return self.min

    def NotIsMerged(self) -> None:
        self.isMerged = False

    def IsMerged(self) -> bool:
        return self.isMerged
