from enum import auto
from strenum import StrEnum


class Mode(StrEnum):
    NONE = auto()
    PHOENIX = auto()
    DOWSING_LOCATOR = auto()
    PICK_ITEMS_ONESHOT = auto()
    PICK_ITEMS_FOREVER = auto()


class Feature(StrEnum):
    BASE = auto()
    DOWSING_LOCATOR = auto()
    ITEM_PICKER = auto()
    GOD = auto()
