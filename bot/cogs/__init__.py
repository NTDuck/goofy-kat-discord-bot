
from .utils import UtilityCog
from .fun import FunCog
from .misc import MiscCog


async def setup(bot):   # register as ext
    cogs = {UtilityCog, FunCog, MiscCog}
    for cog in cogs:
        await bot.add_cog(cog(bot))