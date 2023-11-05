from enum import auto
from strenum import StrEnum

class Mode(StrEnum):
    NONE = auto()
    BROKEN_GURI = auto()
    PICK_ITEMS_ONESHOT = auto()
    PICK_ITEMS_FOREVER = auto()
    EXPERIMENT = auto()