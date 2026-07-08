from typing import ClassVar

from pydantic import BaseModel, ConfigDict

class TimestampInfo(BaseModel):
    features: dict[str, bool]
    states: dict[str, bool]

class IdInfo(BaseModel):
    creator: str = 'Unknown'
    timestamps: dict[int, TimestampInfo]

class NexusModArchive(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(title = "Nexus Mods")

    nexus_ids: dict[int, IdInfo]