import random

from . import Cell
from resources.constants import Status

random.seed()


class Cluster:
    IndexCluster = 0

    def __init__(self):
        self.atoms = []
        self.status = Status.ON_SURFACE
        self.isUp = True
        randway = random.random()
        if randway > 0.5:
            self.isUp = False
        self.clusterNumber = Cluster.IndexCluster + 1
        Cluster.IndexCluster += 1
        self.adjoined = 0
        self.min = Cell()
        self.max = Cell()

    def add_atom(self, atom: Cell) -> None:
        self.atoms.append(atom)
        self.define_rect_border()

    def separation(self) -> None:
        self.status = Status.BREAKING_AWAY
        for j in range(len(self.atoms)):
            self.atoms[j].y += 1
        self.define_rect_border()

    def transition(self, rows: int):  # TODO: убрать из параметров rows (либо переместить, либо перенести управление)
        if self.isUp:
            for j in range(len(self.atoms)):
                self.atoms[j].x += 1 if not self.isUp else -1
            self.define_rect_border()
            if self.max.x < 0 or self.min.x >= rows:
                self.status = Status.OFF_SURFACE

    def merger(self, cluster=None) -> None:
        if not cluster:  # or type(cluster) != 'Cluster':
            return
        for item in cluster.Atoms():
            if item in self.atoms:
                continue
            self.add_atom(item)
        # TODO: продумать логику статусов
        # TODO: возможно метод стоит убрать и перенести управление в композит

    def size(self) -> int:
        return len(self.atoms)

    def number(self) -> int:
        return self.clusterNumber  # TODO: реализовать property ?

    def status(self) -> Status:
        return self.status  # TODO: реализовать property ?

    def is_up(self) -> bool:
        return self.isUp

    def change_way(self) -> None:
        self.isUp = not self.isUp

    def define_rect_border(self) -> None:
        self.adjoined = sum([1 if i.y == 0 else 0 for i in self.atoms])
        self.max.x = max([i.x for i in self.atoms])
        self.max.y = max([i.y for i in self.atoms])
        self.min.x = min([i.x for i in self.atoms])
        self.min.y = min([i.y for i in self.atoms])

        if self.min.y != 0:
            self.status = False  # TODO: продумать логику статусов
        else:
            self.status = True

    def adjoined(self) -> int:
        return self.adjoined  # TODO: реализовать property ?

    def Atoms(self) -> list:
        return self.atoms  # TODO: Удалить метод

    def border_right(self) -> Cell:
        return self.max

    def border_left(self) -> Cell:
        return self.min
