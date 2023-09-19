
from typing import Iterable, List, Tuple, Union

import discord
from redis.asyncio import Redis

from .formatting import voice_state_key_fmt as sk, voice_queue_attr_key_fmt as qak


async def sget(r: Redis, id: int) -> Union[int, None]:
    b: bytes = await r.get(sk(id))
    return int(b.decode())

async def sset(r: Redis, id: int, value: int) -> None:
    return await r.set(sk(id), value)

qattrs = src, name, webpage = ["src", "name", "webpage"]   # necessary audio data, might update in future commits

async def qclear(r: Redis, id: int) -> None:
    for attr in qattrs:
        await r.delete(qak(id, attr))

async def qpop(r: Redis, id: int) -> List[str]:
    values = []
    for ind, attr in enumerate(qattrs):
        b: bytes = await r.lpop(qak(id, attr))
        values[ind] = b.decode()
    return values

async def qappend(r: Redis, id: int, values: Tuple[str, str, str]) -> None:
    for ind, attr in enumerate(qattrs):
        await r.rpush(qak(id, attr), values[ind])   # insert at the end

async def qgetone(r: Redis, id: int, attr: str) -> Union[Iterable[str], None]: 
    bs: List[bytes] = await r.lrange(qak(id, attr), 0, -1)
    return [b.decode() for b in bs]

async def qgetall(r: Redis, id: int) -> List[Union[Iterable[str], None]]:
    return [await qgetone(r, id, attr) for attr in qattrs]   # can be unpacked on iteration using `zip()`; order follows `attrs`

async def qindexone(r: Redis, id: int, attr: str, index: int) -> Union[str, None]:
    b: bytes = await r.lindex(qak(id, attr), index)
    return b.decode()

async def qindexall(r: Redis, id: int, index: int) -> List[Union[str, None]]:
    return [await qindexone(r, id, attr, index) for attr in qattrs]

async def qlen(r: Redis, id: int) -> int:   # could also be used to check if list exists
    return await r.llen(qak(id, name))   # 3 qattrs' lists have identical length

# interaction, for convenience's sake
async def siset(interaction: discord.Interaction, value: int) -> None:
    return await sset(interaction.client.redis_cli, interaction.guild_id, value)

async def siget(interaction: discord.Interaction) -> Union[int, None]:
    return await sget(interaction.client.redis_cli, interaction.guild_id)

async def qiclear(interaction: discord.Interaction) -> None:
    return await qclear(interaction.client.redis_cli, interaction.guild_id)

async def qipop(interaction: discord.Interaction) -> List[str]:
    return await qpop(interaction.client.redis_cli, interaction.guild_id)

async def qiappend(interaction: discord.Interaction, values: Tuple[str, str, str]) -> None:
    return await qappend(interaction.client.redis_cli, interaction.guild_id, values)

async def qigetall(interaction: discord.Interaction) -> List[Union[Iterable[str], None]]:
    return await qgetall(interaction.client.redis_cli, interaction.guild_id)

async def qigetone(interaction: discord.Interaction, attr: str) -> Union[Iterable[str], None]:
    return await qgetone(interaction.client.redis_cli, interaction.guild_id, attr)

async def qiindexall(interaction: discord.Interaction, index: int) -> List[str]:
    return await qindexall(interaction.client.redis_cli, interaction.guild_id, index)

async def qiindexone(interaction: discord.Interaction, attr: str, index: int) -> Union[str, None]:
    return await qindexone(interaction.client.redis_cli, interaction.guild_id, attr, index)

async def qilen(interaction: discord.Interaction) -> int:
    return await qlen(interaction.client.redis_cli, interaction.guild_id)