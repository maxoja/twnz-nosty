from enum import auto
from strenum import StrEnum


class Mode(StrEnum):
    NONE = auto()
    PHOENIX = auto()
    DOWSING_LOCATOR = auto()
    PICK_PEAS_ONESHOT = auto()
    PICK_PEAS_FOREVER = auto()
    BROKEN_GURI = auto()
    PICK_ITEMS_ONESHOT = auto()
    PICK_ITEMS_FOREVER = auto()
    EXPERIMENT = auto()


class Feature(StrEnum):
    BASE = auto()
    DOWSING_LOCATOR = auto()
    PEAS_PICKER = auto()
    GOD = auto()
