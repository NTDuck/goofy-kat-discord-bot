
from collections.abc import Mapping
from typing import Callable, Iterable, List, Optional, Tuple, Union
import asyncio
import random

import discord

from ..const.command import SUCCESS, PENDING
from ..utils.formatter import status_update_prefix as sup


class TicTacToeButton(discord.ui.Button["TicTacToeView"]):
    def __init__(self, _x: int, _y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=_y)
        self._x = _x
        self._y = _y

    def update_on_user_turn(self, view: discord.ui.View):
        # update ui button
        self.style = discord.ButtonStyle.primary
        self.label = "X"
        self.disabled = True
        # update state
        view.state[self._y][self._x] = view.X
        view.current_turn = view.O

    def update_on_bot_turn(self, view: discord.ui.View):
        # update ui button
        self.style = discord.ButtonStyle.primary
        self.label = "O"
        self.disabled = True
        # update state
        view.state[self._y][self._x] = view.O
        view.current_turn = view.X

    def update_on_win(self):
        self.style = discord.ButtonStyle.success

    def update_on_over(self, cheat: bool):
        self.disabled = True
        if cheat:
            self.style = discord.ButtonStyle.danger

    async def callback(self, interaction: discord.Interaction):   # user's turn
        view: TicTacToeView = self.view
        if view.current_turn == view.X:
            self.update_on_user_turn(view)
            content = sup(f"please wait for bot `{interaction.client.user.name}` to make a move", state=PENDING)
        else:
            # cheater!
            await view.on_cheat()
            content = sup(f"user `{interaction.user.name}` cheated. how unfortunate. the game will now end")
        await interaction.response.edit_message(content=content, view=view)
        await asyncio.sleep(1)
        if view.is_game_over():
            await view.on_game_over(interaction)
            return
        await view.bot_move(interaction)


class TicTacToeView(discord.ui.View):
    """
    param `size`: (3, 3) -> (5, 5)
    """
    children: Iterable[TicTacToeButton]
    X = 1
    O = -1
    def __init__(self, size: Tuple[int, int], timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.size = size
        self.state = self.create_state(size)   # mutable
        self.button_mapping = self.create_button_mapping(size)   # immutable
        self.current_turn = self.X   # X goes first
        for item in self.button_mapping.values():
            self.add_item(item)

    @staticmethod
    def create_state(size: Tuple[int, int]) -> List[List[int]]:
        x, y = size
        return [[0 for _ in range(x)] for _ in range(y)]
    
    @staticmethod
    def create_button_mapping(size: Tuple[int, int]) -> Mapping[Tuple[int, int], TicTacToeButton]:
        x, y = size
        return {(_x, _y): TicTacToeButton(_x, _y) for _x in range(x) for _y in range(y)}
    
    @staticmethod
    def check_consec(state: Iterable[Iterable[int]], size: Tuple[int, int]) -> Union[Iterable[Tuple[int, int]], None]:
        """check if a consecutive `3` exists"""
        _vert = lambda _x, _y: [(_x, _y), (_x + 1, _y), (_x + 2, _y)]
        _horiz = lambda _x, _y: [(_x, _y), (_x, _y + 1), (_x, _y + 2)]
        _m_diag = lambda _x, _y: [(_x, _y), (_x + 1, _y + 1), (_x + 2, _y + 2)]
        _a_diag = lambda _x, _y: [(_x, _y), (_x - 1, _y + 1), (_x - 2, _y + 2)]
        
        def is_consec(_l: Iterable[Tuple[int, int]], state: Iterable[Iterable[int]]) -> bool:
            _l = [state[_y][_x] for (_x, _y) in _l]
            return len(set(_l)) == 1 and set(_l) != {0}
        
        def check(_coords: Tuple[int, int], state: Iterable[Iterable[int]], _direction: Callable[[int, int], Iterable[Tuple[int, int]]]) -> Union[Iterable[Tuple[int, int]], None]:
            _x, _y = _coords
            _l = _direction(_x, _y)
            if not is_consec(_l, state):
                return None
            return _l
        
        x, y = size   # assume that x, y >= 3
        # check for consecutive 3s
        # vertical
        for _y in range(y):
            for _x in range(x - 2):
                _l =  check(_coords=(_x, _y), state=state, _direction=_vert)
                if _l is None:
                    continue
                return _l
        # horizontal
        for _x in range(x):
            for _y in range(y - 2):
                _l =  check(_coords=(_x, _y), state=state, _direction=_horiz)
                if _l is None:
                    continue
                return _l
                
        # main diagonal (nw -> se)
        for _y in range(y - 2):
            for _x in range(x - 2):
                _l =  check(_coords=(_x, _y), state=state, _direction=_m_diag)
                if _l is None:
                    continue
                return _l
            
        # anti-diagonal (ne -> sw)
        for _y in range(y - 2):
            for _x in range(2, x):
                _l =  check(_coords=(_x, _y), state=state, _direction=_a_diag)
                if _l is None:
                    continue
                return _l
            
        return None   # unnecessary?

    @staticmethod
    def unassigned_positions(_t: List[List[int]], size: Tuple[int, int]) -> Iterable[Tuple[int, int]]:   # `size` param -> less computational requirement(?)
        # please don't add ai stuff, it'll break poor machine
        x, y = size
        # available choices holds value of 0
        return [(_x, _y) for _x in range(x) for _y in range(y) if _t[_y][_x] == 0]
    
    def bot_choice(self) -> Tuple[int, int]:
        available_choices = self.unassigned_positions(self.state, self.size)
        return random.choice(available_choices)   # for now
    
    async def bot_move(self, interaction: discord.Interaction):
        choice = self.bot_choice()
        # button selected by bot. in an event of NoneType error, don't use dict - seek another solution
        button = self.button_mapping[choice]
        # for item in self.children:
        #     if (item._x, item._y) == choice:
        #         button = item
        button.update_on_bot_turn(self)
        content = sup(f"user `{interaction.user.name}`, your turn", state=SUCCESS)
        await interaction.edit_original_response(content=content, view=self)
        if self.is_game_over():
            await self.on_game_over(interaction)
            return

    def is_game_over(self) -> bool:
        _win_coords = self.check_consec(self.state, self.size)
        if _win_coords is None:   # also makes `winner` None
            return False
        self.win_coords = _win_coords
        self.winner = self.state[_win_coords[0][1]][_win_coords[0][0]]
        return True

    async def on_game_over(self, interaction: discord.Interaction):
        buttons = [self.button_mapping[i] for i in self.win_coords]
        moves = self.size[0]*self.size[1] - sum([i.count(0) for i in self.state])
        for item in buttons:
            item.update_on_win()
        for item in self.children:
            item.update_on_over(cheat=False)
        self.stop()
        content = sup(f"gg `{interaction.user.name}`, you won after `{moves}` moves", state=SUCCESS) if self.winner == self.X else sup(f"`{interaction.user.name}` is such a noob")
        await interaction.edit_original_response(content=content, view=self)

    def on_cheat(self):
        for item in self.children:
            item.update_on_over(cheat=True)
        self.stop()