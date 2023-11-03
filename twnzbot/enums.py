from enum import auto
from strenum import StrEnum

class Mode(StrEnum):
    NONE = auto()
    BROKEN_GURI = auto()
    EXPERIMENT = auto()