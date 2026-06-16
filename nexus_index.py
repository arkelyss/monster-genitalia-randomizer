from typing import ClassVar

from pydantic import BaseModel, ConfigDict

class _TimestampData(BaseModel):
    features: dict[str, bool]
    states: dict[str, bool]

class _IdData(BaseModel):
    creator: str | None = None
    timestamps: dict[str, _TimestampData]

class NexusModIndex(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(title = "Nexus Mod Index")

    description: str = "An index of nexus mods categorized by their IDs and timestamps. Maintains mod information and metadata."
    ids: dict[str, _IdData]


NEXUS_MOD_INDEX: NexusModIndex = NexusModIndex(
    ids = {
        "0000": _IdData(
            creator = "example_name",
            timestamps = {
                "0000000000": _TimestampData(
                    features = {
                        "example_feature_1": True,
                        "example_feature_2": False
                    },
                    states = {
                        "example_state_1": True,
                        "example_state_2": False
                    }
                )
            }
        )
    }
)