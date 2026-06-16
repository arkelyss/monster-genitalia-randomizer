from enum import StrEnum


class GenitaliaFeatures(StrEnum):
    SLIT = "slit"
    PENIS = "penis"
    VULVA = "vulva"
    TESTICLES = "testicles"

class GenitaliaStates(StrEnum):
    ERECT = "erect"
    DISCHARGING = "discharging"
    GLOWING = "glow"