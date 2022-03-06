class Cell:
    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.x = x  # i
        self.y = y  # j

    def __eq__(self, other):
        if isinstance(other, Cell):
            return (self.x == other.x and
                    self.y == other.y)
        return NotImplemented

    # get_x();
    # get_y();
    # set_x(int i);
    # set_y(int j);
