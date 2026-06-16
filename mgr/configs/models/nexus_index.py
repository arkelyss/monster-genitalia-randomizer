from typing import ClassVar

from pydantic import BaseModel, ConfigDict

class TimestampInfo(BaseModel):
    features: dict[str, bool]
    states: dict[str, bool]

class IdInfo(BaseModel):
    creator: str = 'Unknown'
    timestamps: dict[str, TimestampInfo]

class NexusIndex(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(title = "Nexus Config")

    nexus_ids: dict[str, IdInfo]