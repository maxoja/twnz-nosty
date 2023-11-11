import random
import time
from typing import Optional, List, Tuple, Dict

import twnz.bot.base
from twnz import fetch_current_y_x_map_id, image_to_binary_array, walk_to, find_intersection_xy, fetch_map_entities, \
    fetch_player_info, cal_distance, phoenix, find_walk_path_pruned, find_walk_path_granular, is_walkable
from twnz.models import ItemEntity, MapEntity


def get_path_points_yx(api: phoenix.Api, treasure_point_yx):
    cur_y, cur_x, map_id = fetch_current_y_x_map_id(api)
    map_array = image_to_binary_array(map_id)
    path_points = find_walk_path_granular(map_array, (cur_y, cur_x), treasure_point_yx)
    return path_points


class NostyGuriLogic(twnz.bot.base.NostyEmptyLogic):
    STEP_DIST = 8
    REACHED_DIST = 2
    CLICK_COOLDOWN = 0.2

    def __init__(self, *args):
        super(NostyGuriLogic, self).__init__(*args)
        print('init guri logic')
        self.guri_points = []
        self.walk_target: Optional[Tuple[int, int]] = None
        self.next_step_target_yx: Optional[Tuple[int, int]] = None
        self.path_points_yx: List = None
        self.allow_next_click = time.time()

    def reset_states(self):
        self.guri_points = []
        self.walk_target = None
        self.next_step_target_yx = None
        self.path_points_yx = None

    def on_start_clicked(self):
        print('on_start_clicked guri logic')
        pass

    def on_all_tick(self, json_msg: dict):
        if self.walk_target is None:
            return
        if self.next_step_target_yx is None:
            return

        cur_y, cur_x, _ = fetch_current_y_x_map_id(self.api)
        cur_yx = (cur_y, cur_x)

        if cal_distance(self.walk_target, cur_yx) <= NostyGuriLogic.REACHED_DIST:
            self.reset_states()
            return

        if time.time() < self.allow_next_click:
            return
        self.allow_next_click = time.time() + NostyGuriLogic.CLICK_COOLDOWN

        next_i = 0
        for i, yx in enumerate(self.path_points_yx):
            dist = cal_distance(yx, cur_yx)
            if dist >= NostyGuriLogic.STEP_DIST:
                break
            next_i = i
        self.next_step_target_yx = self.path_points_yx[next_i]
        self.path_points_yx = self.path_points_yx[next_i:]
        print('walk to', self.next_step_target_yx)
        self.api.player_walk(*self.next_step_target_yx[::-1])

    def on_send(self, head: str, tail: str):
        if head == 'bp_close':
            print('clear states')
            self.walk_target = None
            self.guri_points = []

    def on_recv(self, head: str, tail: str):
        if self.walk_target is not None:
            return

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

            if treasure_yx is None:
                print("!!!! cannot derive intersection from guri points, please guri more")
                return

            cur_y, cur_x, map_id = fetch_current_y_x_map_id(self.api)
            map_array = image_to_binary_array(map_id)

            if not is_walkable(map_array, treasure_yx[0], treasure_yx[1]):
                print("!!! intersection point is not walkable")
                return

            print("*** intersection from last 2 cracks yx", treasure_yx)
            self.guri_points = []
            self.walk_target = treasure_yx
            self.path_points_yx = get_path_points_yx(self.api, treasure_yx)
            print(self.path_points_yx)
            self.next_step_target_yx = self.path_points_yx[0]


class NostyQuickHandLogic(twnz.bot.base.NostyEmptyLogic):
    DELAY_CHECK = 0
    DELAY_ACT = 0.1
    BUFFER_ACT = 0.05
    PICK_DIST = 2

    def get_next_act_time(self):
        return time.time() + NostyQuickHandLogic.DELAY_ACT + random.random()*NostyQuickHandLogic.BUFFER_ACT

    def on_start_clicked(self):
        print('on_start')
        self.next_act_allow = self.get_next_act_time()
        self.next_check_allow = time.time()
        self.radius = 10
        self.me = fetch_player_info(self.api)
        self.me_yx = (self.me['y'], self.me['x'])
        self.map_ent = fetch_map_entities(self.api)
        self.target_items = [i for i in self.map_ent.items if cal_distance(self.me_yx, (i.y, i.x)) <= self.radius and i.id != -1 and (i.owner_id in [0,-1] or i.owner_id == self.me['id'])]
        self.target_item = self.__get_next_item()
        self.act_queue = []

    def __get_next_item(self) -> Optional[ItemEntity]:
        return self.target_items.pop(0) if len(self.target_items) > 0 else None

    def __check(self):
        latest_map = fetch_map_entities(self.api)
        items_on_map = latest_map.items
        item_ids_on_map = set([i.id for i in items_on_map])

        while self.target_item is not None and self.target_item.id not in item_ids_on_map:
            self.target_item = self.__get_next_item()

        if self.target_item is None:
            if self.ctrl_win.start:
                self.ctrl_win.start_button.click()
            return

        if len(self.act_queue) > 0:
            # is busy
            return

        if time.time() >= self.next_act_allow:
            me_now = fetch_player_info(self.api)
            dist = cal_distance((me_now['y'], me_now['x']), (self.target_item.y, self.target_item.x))
            dist_str = f'{dist:2f}'
            if dist > NostyQuickHandLogic.PICK_DIST:
                # print(self.next_item.id, 'walk to item', dist_str)
                self.api.player_walk(self.target_item.x, self.target_item.y)
            else:
                print(self.target_item.id, 'picking item', dist_str)
                self.api.send_packet(f'get 1 {me_now["id"]} {self.target_item.id}')
            self.next_act_allow = self.get_next_act_time()

    def on_all_tick(self, json_msg: dict):
        if self.target_item is None:
            return
        if time.time() >= self.next_check_allow:
            self.__check()
            self.next_check_allow = time.time() + NostyQuickHandLogic.DELAY_CHECK


class ItemObservation:
    def __init__(self, item: ItemEntity, cooldown: float=30):
        self.item = item
        self.t = time.time()
        self.cooldown = cooldown

    def of_item(self, item: ItemEntity):
        return self.item.id == item.id

    def item_id(self):
        return self.item.id

    def outdated(self):
        return time.time() - self.t >= self.cooldown

    def reset_count(self):
        self.t = time.time()

    def is_in(self, observations: List):
        for o in observations:
            if self.of_item(o.item):
                return True
        return False

    @staticmethod
    def find_obv_of_item(observations: List['ItemObservation'], item: Optional[ItemEntity]) -> Optional['ItemObservation']:
        if item is None:
            return None
        for o in observations:
            if o.of_item(item):
                return o
        return None


def valid_item(i: ItemEntity) -> bool:
    return i.id != -1


def has_maybe_ownership(p: Dict, i: ItemEntity) -> bool:
    return i.owner_id in [0, -1, p['id']]


def has_certain_ownership(p: Dict, i: ItemEntity) -> bool:
    return i.owner_id in [p['id']]
    # return i.owner_id in [p['id']]


def not_mine_for_sure(p: Dict, i: ItemEntity) -> bool:
    return not has_maybe_ownership(p, i)


class NostyQuickHandForeverLogic(NostyQuickHandLogic):
    # TODO 30 second cool down for picked item ignore

    def on_start_clicked(self):
        print('on_start forever')
        self.next_act_allow = self.get_next_act_time()
        self.next_check_allow = time.time()
        self.radius = 1000
        self.target_item = None
        self.others_item_observations: List[ItemObservation] = []
        self.attempted_item_ids: List[int] = []  # we will only attempt an item once
        self.recently_picked_items: List[ItemObservation] = []

    def __get_item_top_candidate(self, latest_map: MapEntity) -> Optional[ItemEntity]:
        me = fetch_player_info(self.api)
        me_y, me_x = me['y'], me['x']
        candidates: List[ItemEntity] = []
        for i in latest_map.items:
            if not valid_item(i):
                continue
            if has_certain_ownership(me, i):
                candidates.append(i)
                continue
            if i.id in self.attempted_item_ids:
                continue
            recent_pick_obv = ItemObservation.find_obv_of_item(self.recently_picked_items, i)
            if recent_pick_obv is not None:
                # checking for success/failure will happen in check method
                continue

            others_item_obv = ItemObservation.find_obv_of_item(self.others_item_observations, i)
            if not_mine_for_sure(me, i):
                if others_item_obv is None:
                    print("observed other's item", i)
                    self.others_item_observations.append(ItemObservation(i))
                    continue
                if others_item_obv.outdated():
                    candidates.append(i)
                    others_item_obv.reset_count()
                    continue
            else:
                # attempt before put it on observation list
                if others_item_obv is None:
                    candidates.append(i)
                    continue
                if others_item_obv.outdated():
                    candidates.append(i)
                    others_item_obv.reset_count()
                    continue

        def s(item: ItemEntity):
            return cal_distance((me_y, me_x), (item.y, item.x))
        candidates.sort(key=s)

        return candidates[0] if len(candidates) > 0 else None

    def __check(self):
        latest_map = fetch_map_entities(self.api)
        if latest_map is None:
            return

        to_remove_rpis = []
        for rpi in self.recently_picked_items:
            if not rpi.outdated():
                # it's not yet ready to check
                continue
            if latest_map.find_item_with_id(rpi.item_id()) is None:
                print('rpi check -> successfully picked item -------')
                self.attempted_item_ids.append(rpi.item_id())
            else:
                print("rpi check -> failed to pick -> add observations", rpi.item)
                self.others_item_observations.append(ItemObservation(rpi.item))
            to_remove_rpis.append(rpi)
        [self.recently_picked_items.remove(rpi) for rpi in to_remove_rpis]

        if self.target_item is not None and (
                self.target_item.id in self.attempted_item_ids or
                ItemObservation.find_obv_of_item(self.recently_picked_items, self.target_item) is not None or
                ItemObservation.find_obv_of_item(self.others_item_observations, self.target_item) is not None or
                latest_map.find_item_with_id(self.target_item.id) is None
        ):
            self.target_item = None

        # always find new closest item
        top_candidate = self.__get_item_top_candidate(latest_map)
        me_now = None
        dist_target = None

        if self.target_item is None:
            self.target_item = top_candidate
            # print('set target from candidate', top_candidate)
        else:
            if top_candidate is not None:
                if self.target_item.id != top_candidate.id:
                    # not already same item
                    me_now = fetch_player_info(self.api)
                    dist_target = cal_distance((self.target_item.y, self.target_item.x), (me_now['y'], me_now['x']))
                    dist_cand = cal_distance((top_candidate.y, top_candidate.x), (me_now['y'], me_now['x']))
                    if dist_cand < dist_target:
                        self.target_item = top_candidate
                        dist_target = dist_cand

        if self.target_item is None:
            # no target and no candidate
            return

        map_ent = latest_map
        if map_ent is None:
            # accidental retrieval failure
            return

        if time.time() >= self.next_act_allow:
            if me_now is None:
                me_now = fetch_player_info(self.api)
            if dist_target is None:
                dist_target = cal_distance((me_now['y'], me_now['x']), (self.target_item.y, self.target_item.x))

            dist_str = f'{dist_target:2f}'
            if dist_target > NostyQuickHandLogic.PICK_DIST:
                print(self.target_item.id, 'walk to item', dist_str)
                self.api.player_walk(self.target_item.x + 1, self.target_item.y + 1)
            else:
                print(self.target_item.id, 'picking item', dist_str)
                self.api.send_packet(f'get 1 {me_now["id"]} {self.target_item.id}')
                self.recently_picked_items.append(ItemObservation(self.target_item, cooldown=2))
                # self.recently_picked_item = self.target_item
                # self.attempted_item_ids.append(self.target_item.id)
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