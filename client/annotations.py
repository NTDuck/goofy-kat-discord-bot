
from collections.abc import Mapping, Iterable
from typing import Any, Union

from .cogs.audio import AudioData


GuildVoiceDataMapping = Mapping[str, Union[bool, Iterable[AudioData]]]
GuildDataMapping = Mapping[str, Union[GuildVoiceDataMapping, Any]]