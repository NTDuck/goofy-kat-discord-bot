
from typing import Iterable, Optional, Tuple

state = [
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
]
size = (5, 5)
def find_adjacent(state: Iterable[Iterable[int]], size: Tuple[int, int]) -> Iterable[Optional[Tuple[int, int]]]:
    """param `size` no smaller than (3, 3)."""
    _adjacent = lambda _x, _y, _d: [(_x + x, _y + y) for x in range(-_d, _d + 1, _d) for y in range(-_d, _d + 1, _d)]
    # param `_d`: distance must be a positive integer
    x, y = size

    _taken = [(_x, _y) for _x in range(x) for _y in range(y) if state[_y][_x] == 1]
    if not _taken:
        return [(_x, _y) for _x in range(x) for _y in range(y)]   # or None?
    
    _adjs = []
    for (_x, _y) in _taken:
        _adjs.extend(_adjacent(_x, _y, 1))
    _adjs = set(_adjs)   # remove duplicates

    tmp = []

    for (_x, _y) in _adjs:
        if _x not in range(x) or _y not in range(y):   # out of range
            tmp.append((_x, _y))
            continue
        if state[_y][_x] != 0:   # not available
            tmp.append((_x, _y))

    return _adjs.difference(tmp)

import random
print(random.choice(find_adjacent(state, size)))