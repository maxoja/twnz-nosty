import random
import time
from typing import Optional, List

import twnz.bot.base
from twnz import fetch_current_y_x_map_id, image_to_binary_array, walk_to, find_intersection_xy, fetch_map_entities, \
    fetch_player_info, cal_distance, phoenix
from twnz.models import ItemEntity


def go_to_treasure(api: phoenix.Api, treasure_point_yx):
    cur_y, cur_x, map_id = fetch_current_y_x_map_id(api)
    map_array = image_to_binary_array(map_id)
    print('go_to_treasure at', treasure_point_yx)
    walk_to(api, map_array, treasure_point_yx)


class NostyGuriLogic(twnz.bot.base.NostyEmptyLogic):
    def __init__(self, *args):
        super(NostyGuriLogic, self).__init__(*args)
        print('on init')
        self.guri_points = []

    def on_start_clicked(self):
        print('on_start')
        pass

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


class NostyQuickHandLogic(twnz.bot.base.NostyEmptyLogic):
    DELAY_CHECK = 0
    DELAY_ACT = 0.15
    BUFFER_ACT = 0.05
    PICK_DIST = 2

    def get_next_act_time(self):
        return time.time() + NostyQuickHandLogic.DELAY_ACT + random.random()*NostyQuickHandLogic.BUFFER_ACT

    def on_start(self):
        print('on_start')
        self.next_act_allow = self.get_next_act_time()
        self.next_check_allow = time.time()
        self.radius = 10
        self.me = fetch_player_info(self.api)
        self.me_yx = (self.me['y'], self.me['x'])
        self.map_ent = fetch_map_entities(self.api)
        self.target_items = [i for i in self.map_ent.items if cal_distance(self.me_yx, (i.y, i.x)) <= self.radius and i.id != -1 and (i.owner_id in [0,-1] or i.owner_id == self.me['id'])]
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
            return

        if len(self.act_queue) > 0:
            # is busy
            return

        if time.time() >= self.next_act_allow:
            me_now = fetch_player_info(self.api)
            dist = cal_distance((me_now['y'], me_now['x']), (self.next_item.y, self.next_item.x))
            dist_str = f'{dist:2f}'
            if dist > NostyQuickHandLogic.PICK_DIST:
                print(self.next_item.id, 'walk to item', dist_str)
                self.api.player_walk(self.next_item.x, self.next_item.y)
            else:
                print(self.next_item.id, 'picking item', dist_str)
                self.api.send_packet(f'get 1 {me_now["id"]} {self.next_item.id}')
            self.next_act_allow = self.get_next_act_time()

    def on_all_tick(self, json_msg: dict):
        if self.next_item is None:
            return
        if time.time() >= self.next_check_allow:
            self.__check()
            self.next_check_allow = time.time() + NostyQuickHandLogic.DELAY_CHECK


class NostyQuickHandForeverLogic(NostyQuickHandLogic):
    # TODO 30 second cool down for picked item ignore

    def on_start_clicked(self):
        print('on_start forever')
        self.next_act_allow = self.get_next_act_time()
        self.next_check_allow = time.time()
        self.radius = 1000
        self.act_queue = []
        self.next_item = None
        self.picked_items: List[ItemEntity] = []

    def get_picked_ids(self):
        return [i.id for i in self.picked_items]

    def __get_next_item(self) -> Optional[ItemEntity]:
        latest_map = fetch_map_entities(self.api)
        me = fetch_player_info(self.api)
        me_y, me_x = me['y'], me['x']
        items_on_map = [ i for i in latest_map.items if i.id != -1 and (i.owner_id in [0,-1] or i.owner_id == me['id']) and i.id not in self.get_picked_ids()]
        def s(item: ItemEntity):
            return cal_distance((me_y, me_x), (item.y, item.x))
        items_on_map.sort(key=s)
        return items_on_map.pop(0) if len(items_on_map) > 0 else None

    def __check(self):
        if self.next_item is not None and self.next_item.id in self.get_picked_ids():
            self.next_item = None
        if self.next_item is None:
            self.next_item = self.__get_next_item()
        if self.next_item is None:
            return


        map_ent = fetch_map_entities(self.api)
        if map_ent is None:
            return

        to_remove = []
        for i in self.picked_items:
            same_item = map_ent.find_item_with_id(i.id)
            if same_item is None:
                to_remove.append(i)
                continue
            if same_item.owner_id != i.owner_id:
                to_remove.append(i)
        for i in to_remove:
            self.picked_items.remove(i)


        if self.next_item.id in [i.id for i in map_ent.items]:
            self.next_item = [i for i in map_ent.items if i.id == self.next_item.id][0]
        else:
            self.next_item = None
            return

        if time.time() >= self.next_act_allow:
            me_now = fetch_player_info(self.api)
            dist = cal_distance((me_now['y'], me_now['x']), (self.next_item.y, self.next_item.x))
            dist_str = f'{dist:2f}'
            if dist > NostyQuickHandLogic.PICK_DIST:
                print(self.next_item.id, 'walk to item', dist_str)
                self.api.player_walk(self.next_item.x+1, self.next_item.y+1)
            else:
                print(self.next_item.id, 'picking item', dist_str)
                self.api.send_packet(f'get 1 {me_now["id"]} {self.next_item.id}')
                self.picked_items.append(self.next_item)
            self.next_act_allow = self.get_next_act_time()

    def on_all_tick(self, json_msg: dict):
        if time.time() >= self.next_check_allow:
            self.__check()
            self.next_check_allow = time.time() + NostyQuickHandLogic.DELAY_CHECK


class NostyExperimentLogic(twnz.bot.base.NostyEmptyLogic):

    def on_start_clicked(self):
        pass

    def on_recv(self, head: str, tail: str):
        pass