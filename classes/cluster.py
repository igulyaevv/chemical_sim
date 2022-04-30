import random

from . import Cell
from resources.constants import Status

random.seed()


class Cluster:
    IndexCluster = 0

    def __init__(self):
        self.atoms = []
        self._status = Status.ON_SURFACE
        self._number = Cluster.IndexCluster + 1
        Cluster.IndexCluster += 1
        self._adjoined = 0
        self.min = Cell()
        self.max = Cell()

    def add_atom(self, atom: Cell) -> None:
        self.atoms.append(atom)
        self.define_rect_border()

    def separation(self) -> None:
        self._status = Status.BREAKING_AWAY
        for j in range(len(self.atoms)):
            self.atoms[j].y += 1
        self.define_rect_border()

    def transition(self, rows: int):  # TODO: убрать из параметров rows (либо переместить, либо перенести управление)
        for j in range(len(self.atoms)):
            self.atoms[j].x += 1 if self._status == Status.DOWN_ALONG_SURFACE else -1
        self.define_rect_border()
        if self.max.x < 0 or self.min.x >= rows:
            self._status = Status.OFF_SURFACE

    def merger(self, cluster) -> None:
        for item in cluster.Atoms():
            if item in self.atoms:
                continue
            self.add_atom(item)
        # TODO: продумать логику статусов
        # TODO: возможно метод стоит убрать и перенести управление в композит

    def size(self) -> int:
        return len(self.atoms)

    @property
    def number(self) -> int:
        return self._number

    @property
    def status(self) -> Status:
        return self._status

    def define_rect_border(self) -> None:
        self._adjoined = sum([1 if i.y == 0 else 0 for i in self.atoms])
        self.max.x = max([i.x for i in self.atoms])
        self.max.y = max([i.y for i in self.atoms])
        self.min.x = min([i.x for i in self.atoms])
        self.min.y = min([i.y for i in self.atoms])

        if self.min.y != 0:
            self._status = False  # TODO: продумать логику статусов
        else:
            self._status = True

    @property
    def adjoined(self) -> int:
        return self._adjoined

    def border_right(self) -> Cell:
        return self.max

    def border_left(self) -> Cell:
        return self.min
