import random
import time
from typing import Optional, List

import twnzbot.base
from phoenixapi import phoenix
from twnzbot.enums import Mode
from twnzlib import fetch_current_y_x_map_id, image_to_binary_array, walk_to, find_intersection_xy, fetch_map_entities, \
    fetch_player_info, cal_distance
from twnzlib.models import ItemEntity


def go_to_treasure(api: phoenix.Api, treasure_point_yx):
    cur_y, cur_x, map_id = fetch_current_y_x_map_id(api)
    map_array = image_to_binary_array(map_id)
    print('go_to_treasure at', treasure_point_yx)
    walk_to(api, map_array, treasure_point_yx)


class NostyExperimentLogic(twnzbot.base.NostyEmptyLogic):
    def get_mode(self):
        return Mode.EXPERIMENT

    def on_start(self):
        pass

    def on_recv(self, head: str, tail: str):
        pass