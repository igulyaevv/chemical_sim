class Cell:
    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.x = x  # i
        self.y = y  # j

    def __eq__(self, other):
        if isinstance(other, Cell):
            return (self.x == other.x and
                    self.y == other.y)
        return NotImplemented

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def set_x(self, i: int = None):
        self.x = i

    def set_y(self, j: int = None):
        self.y = j
