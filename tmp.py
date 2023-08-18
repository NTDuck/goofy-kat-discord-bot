from typing import Iterable, Optional, Tuple, Union, Callable


def check_consec(state: Iterable[Iterable[int]], size: Tuple[int, int]) -> Union[Iterable[Tuple[int, int]], None]:
    """check if a consecutive `3` exists"""
    _vert = lambda _x, _y: [(_x, _y), (_x + 1, _y), (_x + 2, _y)]
    _horiz = lambda _x, _y: [(_x, _y), (_x, _y + 1), (_x, _y + 2)]
    _m_diag = lambda _x, _y: [(_x, _y), (_x + 1, _y + 1), (_x + 2, _y + 2)]
    _a_diag = lambda _x, _y: [(_x, _y), (_x - 1, _y + 1), (_x - 2, _y + 2)]
    
    def is_consec(_l: Iterable[Tuple[int, int]], state: Iterable[Iterable[int]]) -> bool:
        """check if all elements of the array holds the same non-zero value."""
        _l = [state[_y][_x] for (_x, _y) in _l]
        return len(set(_l)) == 1 and set(_l) != {0}
    
    def select_origin_coords(_ex: int, _ey: int, _sx: Optional[int] = 0,_sy: Optional[int] = 0) -> Iterable[Tuple[int, int]]:
        """return all origin coords within specified range."""
        return [(_x, _y) for _x in range(_sx, _ex) for _y in range(_sy, _ey)]
    
    def select_arrs(_coords: Tuple[int, int], _direction: Callable[[int, int], Iterable[Tuple[int, int]]]) -> Iterable[Tuple[int, int]]:
        """return a 3-element array from the original point."""
        _x, _y = _coords
        _l = _direction(_x, _y)
        return _l
        # return _direction(_coords[0], _coords[1])
    
    x, y = size   # assume that x, y >= 3
    # check for consecutive 3s
    # vertical
    for _y in range(y):
        for _x in range(x - 2):
            _l =  select_arrs(_coords=(_x, _y), _direction=_vert)
            if not is_consec(_l, state):
                continue
            return _l
    
    # horizontal
    for _x in range(x):
        for _y in range(y - 2):
            _l =  select_arrs(_coords=(_x, _y), _direction=_horiz)
            if not is_consec(_l, state):
                continue
            return _l
            
    # main diagonal (nw -> se)
    for _y in range(y - 2):
        for _x in range(x - 2):
            _l =  select_arrs(_coords=(_x, _y), _direction=_m_diag)
            if not is_consec(_l, state):
                continue
            return _l
        
    # anti-diagonal (ne -> sw)
    for _y in range(y - 2):
        for _x in range(2, x):
            _l =  select_arrs(_coords=(_x, _y), _direction=_a_diag)
            if not is_consec(_l, state):
                continue
            return _l
        
    return None   # unnecessary?


def select_arrs(size: Tuple[int, int], n: int) -> Union[Iterable[Tuple[Tuple[int, int]]], None]:
    """
    returns all `n`-sized arrays within `state`.
    \n`n`: the number of elements of same value required in a row/column/diagonal to achieve victory.
    """
    def _origins(_ex: int, _ey: int, _sx: Optional[int] = 0,_sy: Optional[int] = 0) -> Iterable[Tuple[int, int]]:
        """return all origin coords within specified range."""
        return [(_x, _y) for _x in range(_sx, _ex) for _y in range(_sy, _ey)]
    
    _vert = lambda _x, _y, n: [(_x + _n, _y) for _n in range(n)]
    _horiz = lambda _x, _y, n: [(_x, _y + _n) for _n in range(n)]
    _m_diag = lambda _x, _y, n: [(_x + _n, _y + _n) for _n in range(n)]
    _a_diag = lambda _x, _y, n: [(_x - _n, _y + _n) for _n in range(n)]

    x, y = size
    if x < n or y < n:
        return None

    # visit previous commit to figure out what this does
    vert_arrs = [_vert(_x, _y, n) for (_x, _y) in _origins(x - n + 1, y)]
    print("v: ", vert_arrs)
    horiz_arrs = [_horiz(_x, _y, n) for (_x, _y) in _origins(x, y - n + 1)]
    print("h: ", horiz_arrs)
    m_diag_arrs = [_m_diag(_x, _y, n) for (_x, _y) in _origins(x - n + 1, y - n + 1)]
    print("m: ", m_diag_arrs)
    a_diag_arrs = [_a_diag(_x, _y, n) for (_x, _y) in _origins(x, y - n + 1, _sx=n - 1)]
    print("a: ", a_diag_arrs)
    
    return vert_arrs + horiz_arrs + m_diag_arrs + a_diag_arrs


def is_consec(_l: Iterable[Tuple[int, int]], state: Iterable[Iterable[int]]) -> bool:
    """check if all elements of the array holds the same non-zero value."""
    _l = [state[_y][_x] for (_x, _y) in _l]
    return len(set(_l)) == 1 and set(_l) != {0}

t = [
    [0, 0, 1],
    [0, 1, 0],
    [1, 0, 0],
]
size = (3, 3)

for arr in select_arrs(size, 3):
    if is_consec(arr, t):
        print(arr)