
from collections.abc import Set
from typing import Iterable, Optional, Tuple, Union
from ..const.tictactoe import X, O


class TicTacToeUtils:
    def create_l_coords(self, size: Tuple[int, int], n: int) -> Union[Iterable[Tuple[Tuple[int, int]]], None]:
        """
        returns an immutable list containing all `n`-sized arrays from specified `size`.
        \n`n`: the number of elements of same value required in a row/column/diagonal to achieve victory.
        """
        def _origins(_ex: int, _ey: int, _sx: Optional[int] = 0, _sy: Optional[int] = 0) -> Iterable[Tuple[int, int]]:
            """
            return all origin coords within specified range.
            \n`origin` coords are points based on which l_coords can be developed.
            """
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
        
        return vert_arrs + horiz_arrs + m_diag_arrs + a_diag_arrs   # bad convention
    
    def find_matching_l_coords(self, _l_coords: Iterable[Tuple[int, int]], state: Iterable[Iterable[int]], _target: int, _target_count: Optional[int] = None, _residue: Optional[int] = None) -> Union[Iterable[Tuple[int, int]], None]:
        """
        \nparam `_l`: list of coordinates.
        \ncheck if an array contains exactly `_target_count` number of elements holding value `_target`, and optionally if other elements hold the same value `_residue`.
        \nreturns the list of `_target` coordinates.
        """
        n = len(_l_coords)
        if _target_count is None:
            _target_count = n

        _vals = [state[_y][_x] for (_x, _y) in _l_coords]
        _inds = [_ind for _ind, _val in enumerate(_vals) if _val == _target]

        if not all([
            _target_count == len(_inds),
            _residue is None or _vals.count(_residue) == n - _target_count,
        ]):
            return None
        return [_l_coords[_ind] for _ind in _inds]

    def find_consec(self, state: Iterable[Iterable[int]], arrs: Iterable[Tuple[Tuple[int, int]]]) -> Union[Iterable[Tuple[int, int]], int, None]:
        """
        check if an array containing `n` consecutive elements exists.
        \nparam `arrs` is usually the return value of `self.create_l_coords`.
        """
        for _l_coords in arrs:
            for _target in {X, O}:
                _consec_l_coords = self.find_matching_l_coords(_l_coords=_l_coords, state=state, _target=_target)
                if _consec_l_coords is not None:
                    return _consec_l_coords, _target
        return None, None
    
    def find_threat(self, state: Iterable[Iterable[int]], arrs: Iterable[Tuple[Tuple[int, int]]]) -> Iterable[Optional[Tuple[int, int]]]:
        """returns the list of `_l_coords` marked as `threat` (`n - 1` elements holding opponent's value, 1 element holding `0` value),"""
        results = []
        for _l_coords in arrs:
            _threat_l_coords = self.find_matching_l_coords(_l_coords=_l_coords, state=state, _target=0, _target_count=1, _residue=X)
            if _threat_l_coords is None:
                continue
            results.extend(_threat_l_coords)   # returns exactly an Iterable with 1 sole element being the target coordinates therefore unpacked for convenience
        return results

    def find_opportunity(self, state: Iterable[Iterable[int]], arrs: Iterable[Tuple[Tuple[int, int]]]) -> Iterable[Optional[Tuple[int, int]]]:
        """returns the list of `_l_coords` marked as `opportunity` (`n - 1` elements holding self value, 1 element holding `0` value),"""
        results = []
        for _l_coords in arrs:
            _opportunity_l_coords = self.find_matching_l_coords(_l_coords=_l_coords, state=state, _target=0, _target_count=1, _residue=O)
            if _opportunity_l_coords is None:
                continue
            results.extend(_opportunity_l_coords)
        return results
    
    def find_adjacent(self, state: Iterable[Iterable[int]], size: Tuple[int, int], _target: int) -> Set[Optional[Tuple[int, int]]]:
        """param `size` no smaller than (3, 3)."""
        _adjacent = lambda _x, _y, _d: [(_x + x, _y + y) for x in range(-_d, _d + 1, _d) for y in range(-_d, _d + 1, _d)]
        # param `_d`: distance must be a positive integer
        x, y = size

        _occupied = [(_x, _y) for _x in range(x) for _y in range(y) if state[_y][_x] == _target]
        if not _occupied:
            return {}
        
        adjacents = []
        for (_x, _y) in _occupied:
            adjacents.extend(_adjacent(_x, _y, 1))
        adjacents = set(adjacents)   # remove duplicates

        tmp = []   # done manually - list comprehension somehow does not work

        for (_x, _y) in adjacents:
            if _x not in range(x) or _y not in range(y):   # out of range
                tmp.append((_x, _y))
                continue
            if state[_y][_x] != 0:   # not available
                tmp.append((_x, _y))

        return adjacents.difference(tmp)

    def find_available(self, state: Iterable[Iterable[int]], size: Tuple[int, int]) -> Iterable[Tuple[int, int]]:
        """returns the list of available coordinates (holding the value `0`)."""
        x, y = size
        # available choices holds value of 0
        return [(_x, _y) for _x in range(x) for _y in range(y) if state[_y][_x] == 0]
    
    # @staticmethod
    # def 