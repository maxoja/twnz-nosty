import random
import time
from typing import Optional

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


class NostyGuriLogic(twnzbot.base.NostyEmptyLogic):
    def get_mode(self):
        return Mode.BROKEN_GURI

    def on_start(self):
        self.guri_points = []

    def on_recv(self, head: str, tail: str):
        if head != 'hidn':
            return

        print("[RECV]:", head, tail)
        _, deg, x, y = eval('('+','.join(tail.split()) + ')')
        self.guri_points.append((y, x, deg))
        print("*** hidn received, saving a marker yx", self.guri_points[-1])
        print(self.guri_points)

        if len(self.guri_points) > 2:
            self.guri_points = self.guri_points[1:]
        if len(self.guri_points) >= 2:
            cur_y, cur_x, map_id = fetch_current_y_x_map_id(self.api)
            map_array = image_to_binary_array(map_id)
            treasure_yx = find_intersection_xy(self.guri_points[0], self.guri_points[1], map_array.shape[0])
            print("*** intersection from last 2 cracks yx", treasure_yx)
            print("walking ")
            go_to_treasure(self.api, treasure_yx)
            self.guri_points = []


class NostyQuickHandLogic(twnzbot.base.NostyEmptyLogic):
    DELAY_CHECK = 0
    DELAY_ACT = 0.15
    BUFFER_ACT = 0.05
    PICK_DIST = 2

    def get_mode(self):
        return Mode.ITEM_PICK_QUICK_HAND

    def get_next_act_time(self):
        return time.time() + NostyQuickHandLogic.DELAY_ACT + random.random()*NostyQuickHandLogic.BUFFER_ACT

    def on_start(self):
        self.next_act_allow = self.get_next_act_time()
        self.next_check_allow = time.time()
        self.radius = 10
        self.me = fetch_player_info(self.api)
        self.me_yx = (self.me['y'], self.me['x'])
        self.map_ent = fetch_map_entities(self.api)
        self.target_items = [i for i in self.map_ent.items if cal_distance(self.me_yx, (i.y, i.x)) <= self.radius]
        self.next_item = self.__get_next_item()
        self.act_queue = []

    def __get_next_item(self) -> Optional[ItemEntity]:
        return self.target_items.pop(0) if len(self.target_items) > 0 else None

    def __check(self):
        latest_map = fetch_map_entities(self.api)
        items_on_map = latest_map.items
        item_ids_on_map = set([i.id for i in items_on_map])

        while self.next_item is not None and self.next_item.id not in item_ids_on_map:
            self.next_item = self.__get_next_item()

        if self.next_item is None:
            if self.ctrl_win.start:
                self.ctrl_win.start_button.click()
            # no more items to work on
            return
        if len(self.act_queue) > 0:
            # is busy
            return

        if time.time() >= self.next_act_allow:
            me_now = fetch_player_info(self.api)
            if cal_distance((me_now['y'], me_now['x']), (self.next_item.y, self.next_item.x)) > NostyQuickHandLogic.PICK_DIST:
                self.api.player_walk(self.next_item.x, self.next_item.y)
            else:
                self.api.send_packet(f'get 1 {me_now["id"]} {self.next_item.id}')
            self.next_act_allow = self.get_next_act_time()

    def on_all_tick(self, json_msg: dict):
        if self.next_item is None:
            return
        if time.time() >= self.next_check_allow:
            self.__check()
            self.next_check_allow = time.time() + NostyQuickHandLogic.DELAY_CHECK


class NostyExperimentLogic(twnzbot.base.NostyEmptyLogic):
    def get_mode(self):
        return Mode.EXPERIMENT

    def on_start(self):
        pass

    def on_recv(self, head: str, tail: str):
        pass