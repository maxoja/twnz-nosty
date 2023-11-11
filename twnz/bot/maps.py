from typing import Type, List

from twnz.bot.base import NostyEmptyLogic
from twnz.bot.enums import Mode, Feature
from twnz.bot.more import NostyQuickHandForeverLogic, NostyGuriLogic
from twnz.bot.qol import NostyPhoenixLogic


admin_features = [m for m in Mode if m not in [Mode.NONE]]

__feature_to_modes_map = {
    Feature.GOD: admin_features,
    Feature.BASE: [Mode.PHOENIX],
    Feature.DOWSING_LOCATOR: [Mode.DOWSING_LOCATOR],
    # Feature.ITEM_PICKER: [Mode.PICK_ITEMS_ONESHOT, Mode.PICK_ITEMS_FOREVER],
    Feature.ITEM_PICKER: [Mode.PICK_ITEMS_FOREVER],
}

__mode_to_logic_map = {
    Mode.NONE: NostyEmptyLogic,
    Mode.PHOENIX: NostyPhoenixLogic,
    Mode.DOWSING_LOCATOR: NostyGuriLogic,
    Mode.PICK_ITEMS_FOREVER: NostyQuickHandForeverLogic,
}


def feature_to_modes(feature: Feature) -> List[Mode]:
    if feature not in __feature_to_modes_map:
        return []
    return __feature_to_modes_map[feature]


def mode_to_logic_class(mode: Mode) -> Type[NostyEmptyLogic]:
    if mode not in __mode_to_logic_map:
        raise Exception("Undefined map for mode " + str(mode) + " enum, no logic class defined")
    return __mode_to_logic_map[mode]
