
from typing import Iterable, Optional, Tuple
import asyncio
import random
import logging

import discord

from . import logger
from ..const.command import SUCCESS, PENDING, ANXIOUS
from ..const.tictactoe import X, O, N
from ..utils.formatter import status_update_prefix as sup
from ..utils.tictactoe import TicTacToeUtils


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
        view.state[self._y][self._x] = X
        view.current_turn = O

    def update_on_bot_turn(self, view: discord.ui.View):
        # update ui button
        self.style = discord.ButtonStyle.primary
        self.label = "O"
        self.disabled = True
        # update state
        view.state[self._y][self._x] = O
        view.current_turn = X

    def update_on_win(self):
        self.style = discord.ButtonStyle.success

    def update_on_over(self, cheat: bool):
        self.disabled = True
        if cheat:
            self.style = discord.ButtonStyle.danger

    async def callback(self, interaction: discord.Interaction):   # user's turn
        view: TicTacToeView = self.view
        # not tested
        if interaction.user.id != view.user.id:   # hey, only 1 player!
            await interaction.response.send_message(content=sup(f"`{interaction.user.name}`, you are not allowed to play - this is `{view.user.name}`'s only"))
            return
        if view.current_turn == X:
            self.update_on_user_turn(view)
            content = sup(f"please wait for bot `{interaction.client.user.name}` to make a move", state=PENDING)
        else:
            view.cheated = True
        view.moves += 1
        await interaction.response.edit_message(content=content, view=view)
        if view.is_game_over():
            await view.on_game_over(interaction)
            return
        await view.bot_move(interaction)

        logger.debug(f"button ({self._x}, {self._y}) invoked by {interaction.user.name} (uid: {interaction.user.id})")


class TicTacToeView(discord.ui.View, TicTacToeUtils):
    """
    param `size`: (3, 3) -> (5, 5)
    """
    children: Iterable[TicTacToeButton]
    def __init__(self, user: discord.User, size: Tuple[int, int], timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.user = user
        self.size = size
        self.logger = logger.getChild(self.__class__.__name__)

        x, y = size
        self.state = [[0 for _ in range(x)] for _ in range(y)]   # mutable
        self.l_coords = self.create_l_coords(size=self.size, n=N)   # immutable
        self.button_mapping = {(_x, _y): TicTacToeButton(_x, _y) for _x in range(x) for _y in range(y)}   # immutable

        self.current_turn = X   # X goes first
        self.moves = 0
        self.cheated = False
        self.acknowledge_defeat = False

        for item in self.button_mapping.values():
            self.add_item(item)

    def bot_choice(self) -> Tuple[int, int]:
        """
        priority:
        if opponent has `n - 1` positions in any `n`-sized array -> intercept | else
        \nif self has `n - 1` positions in any `n`-sized array -> complete self arr | else
        \nif center positions are not taken by opponents -> prioritize center | else
        \nprioritize adjacent positions
        \nrandom
        """
        available_choices = self.find_available(self.state, self.size)

        threats = self.find_threat(self.state, self.l_coords)
        if len(threats) > 1:
            self.acknowledge_defeat = True
        if threats:
            return random.choice(threats)

        opportunities = self.find_opportunity(self.state, self.l_coords)
        if opportunities:
            return random.choice(opportunities)
        
        opponent_adjacents = self.find_adjacent(self.state, self.size, _target=X)
        if opponent_adjacents:
            return random.choice(list(opponent_adjacents))
        
        self_adjacents = self.find_adjacent(self.state, self.size, _target=O)
        if self_adjacents:
            return random.choice(list(self_adjacents))
        
        return random.choice(available_choices)   # last resort

    async def bot_move(self, interaction: discord.Interaction):
        if self.cheated:
            self.on_cheat()
            content = sup(f"user `{interaction.user.name}` cheated. shame on you")
            await interaction.edit_original_response(content=content, view=self)
            return
        choice = self.bot_choice()
        # button selected by bot. in an event of NoneType error, don't use dict - seek another solution
        # for item in self.children:
        #     if (item._x, item._y) == choice:
        #         button = item
        button = self.button_mapping[choice]
        button.update_on_bot_turn(self)
        self.moves += 1
        content = sup(f"user `{interaction.user.name}`, your turn", state=SUCCESS) if not self.acknowledge_defeat else sup(f"user `{interaction.user.name}`, become ||elden lord||", state=ANXIOUS)
        await asyncio.sleep(1)
        await interaction.edit_original_response(content=content, view=self)
        if self.is_game_over():
            await self.on_game_over(interaction)
            return

    def is_game_over(self) -> bool:
        _win_l_coords, winner = self.find_consec(self.state, self.l_coords)
        if _win_l_coords is None:   # also makes `winner` None
            return False
        self._win_l_coords = _win_l_coords
        self.winner = winner
        return True

    async def on_game_over(self, interaction: discord.Interaction):
        buttons = [self.button_mapping[i] for i in self._win_l_coords]
        # moves = self.size[0]*self.size[1] - sum([i.count(0) for i in self.state])
        for item in buttons:
            item.update_on_win()
        for item in self.children:
            item.update_on_over(cheat=False)
        self.stop()
        content = sup(f"gg `{interaction.user.name}`, you won after `{self.moves}` moves", state=SUCCESS) if self.winner == X else sup(f"`{interaction.user.name}` is such a noob")
        await interaction.edit_original_response(content=content, view=self)

    def on_cheat(self):
        for item in self.children:
            item.update_on_over(cheat=True)
        self.stop()