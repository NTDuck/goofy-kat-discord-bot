
from typing import Iterable, List, Optional, Tuple, Union


class TicTacToeUtils:
    @staticmethod
    def select_arrs(size: Tuple[int, int], n: int) -> Union[Iterable[Tuple[Tuple[int, int]]], None]:
        """
        returns all `n`-sized arrays within `state`.
        \n`n`: the number of elements of same value required in a row/column/diagonal to achieve victory.
        """
        def _origins(_ex: int, _ey: int, _sx: Optional[int] = 0, _sy: Optional[int] = 0) -> Iterable[Tuple[int, int]]:
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
        horiz_arrs = [_horiz(_x, _y, n) for (_x, _y) in _origins(x, y - n + 1)]
        m_diag_arrs = [_m_diag(_x, _y, n) for (_x, _y) in _origins(x - n + 1, y - n + 1)]
        a_diag_arrs = [_a_diag(_x, _y, n) for (_x, _y) in _origins(x, y - n + 1, _sx=n - 1)]
        
        return vert_arrs + horiz_arrs + m_diag_arrs + a_diag_arrs

    @staticmethod
    def check_consec(state: Iterable[Iterable[int]], arrs: Iterable[Tuple[Tuple[int, int]]]) -> Union[Iterable[Tuple[int, int]], None]:
        """check if a consecutive `n` exists"""
        def is_consec(_l: Iterable[Tuple[int, int]], state: Iterable[Iterable[int]]) -> bool:
            """check if all elements of the array holds the same non-zero value."""
            _l = [state[_y][_x] for (_x, _y) in _l]
            return len(set(_l)) == 1 and set(_l) != {0}
        for arr in arrs:
            if not is_consec(arr, state=state):
                continue
            return arr

    @staticmethod
    def unassigned_positions(_t: List[List[int]], size: Tuple[int, int]) -> Iterable[Tuple[int, int]]:   # `size` param -> less computational requirement(?)
        # please don't add ai stuff, it'll break poor machine
        x, y = size
        # available choices holds value of 0
        return [(_x, _y) for _x in range(x) for _y in range(y) if _t[_y][_x] == 0]