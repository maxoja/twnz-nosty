import random
import time
from typing import Optional, List, Tuple, Dict

import twnz.bot.base
from twnz import fetch_current_y_x_map_id, image_to_binary_array, walk_to, find_intersection_xy, fetch_map_entities, \
    fetch_player_info, cal_distance, phoenix, find_walk_path_granular, is_walkable, \
    find_nearest_walkable_cell, TimeCheck
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
                print("!!! intersection point is not walkable", treasure_yx)
                treasure_yx = find_nearest_walkable_cell(map_array, *treasure_yx)
                print('override that to', treasure_yx)

            print("*** intersection from last 2 cracks yx", treasure_yx)
            self.guri_points = []
            self.walk_target = treasure_yx
            self.path_points_yx = get_path_points_yx(self.api, treasure_yx)
            print(self.path_points_yx)
            self.next_step_target_yx = self.path_points_yx[0]


class ItemTimer:
    def __init__(self, item: ItemEntity, cooldown: float = 29):
        self.item = item
        self.t = time.time()
        self.cooldown = cooldown

    def of_item(self, item: ItemEntity):
        return self.item.id == item.id

    def item_id(self):
        return self.item.id

    def timeout(self):
        return time.time() - self.t >= self.cooldown

    def reset_count(self):
        self.t = time.time()

    def is_in(self, observations: List):
        for o in observations:
            if self.of_item(o.item):
                return True
        return False

    @staticmethod
    def find_obv_of_item(observations: List['ItemTimer'], item: Optional[ItemEntity]) -> Optional['ItemTimer']:
        if item is None:
            return None
        for o in observations:
            if o.of_item(item):
                return o
        return None


class ItemTempBan(ItemTimer):
    def __init__(self, item: ItemEntity):
        super(ItemTempBan, self).__init__(item)
        self.retried = False

    def ready_for_second_chance(self):
        return self.timeout()

    def mark_retried(self):
        if not self.ready_for_second_chance():
            raise Exception()
        self.retried = True

    def reset_count(self):
        raise Exception("Item Ban can't be reset")

    def gave_up(self):
        return self.timeout() and self.retried


def valid_item(i: ItemEntity) -> bool:
    return i.id != -1


def has_maybe_ownership(p: Dict, i: ItemEntity) -> bool:
    return i.owner_id in [0, -1, p['id']]


def has_certain_ownership(p: Dict, i: ItemEntity) -> bool:
    return i.owner_id in [p['id']]
    # return i.owner_id in [p['id']]


def not_mine_for_sure(p: Dict, i: ItemEntity) -> bool:
    return not has_maybe_ownership(p, i)


class NostyQuickHandForeverLogic(twnz.bot.base.NostyEmptyLogic):
    DELAY_CHECK = 0.05
    DELAY_ACT = 0.1
    BUFFER_ACT = 0.05
    PICK_DIST = 2

    def on_start_clicked(self):
        print('on_start forever')
        self.next_act_timer = TimeCheck(NostyQuickHandForeverLogic.DELAY_ACT, swing=NostyQuickHandForeverLogic.BUFFER_ACT)
        self.next_check_timer = TimeCheck(NostyQuickHandForeverLogic.DELAY_CHECK)
        self.target_item = None
        self.banned_items: List[ItemTempBan] = []
        self.items_to_be_verified: List[ItemTimer] = []

    def __add_ban_new_others_items(self, me: Dict, latest_map: MapEntity):
        for i in latest_map.items:
            if ItemTimer.find_obv_of_item(self.banned_items, i) is None:
                if not_mine_for_sure(me, i):
                    print('adding ban', i)
                    self.banned_items.append(ItemTempBan(i))

    def __get_item_top_candidate(self, me: dict, latest_map: MapEntity) -> Optional[ItemEntity]:
        me_y, me_x = me['y'], me['x']
        candidates: List[ItemEntity] = []
        for i in latest_map.items:
            if not valid_item(i):
                continue
            if has_certain_ownership(me, i):
                candidates.append(i)
                continue
            temp_ban: ItemTempBan = ItemTimer.find_obv_of_item(self.banned_items, i)
            if temp_ban is not None:
                if not temp_ban.ready_for_second_chance() or temp_ban.gave_up():
                    continue
            if ItemTimer.find_obv_of_item(self.items_to_be_verified, i) is not None:
                continue
            candidates.append(i)

        def s(item: ItemEntity):
            return cal_distance((me_y, me_x), (item.y, item.x))

        candidates.sort(key=s)
        return candidates[0] if len(candidates) > 0 else None

    def __give_second_chance_to_banned_if_timout(self):
        for b in self.banned_items:
            if b.timeout():
                if b not in self.second_chance_items:
                    self.second_chance_items.append(b.item)
                    b.reset_count() # may b not

    def __process_recently_picked_items_and_remove_from_list(self, latest_map: MapEntity):
        new_queue = []
        for to_check in self.items_to_be_verified:
            if not to_check.timeout():
                new_queue.append(to_check)
                continue
            if latest_map.find_item_with_id(to_check.item_id()) is None:
                print('pickup check -> item is gone -> successfully picked item')
                continue
            temp_ban: ItemTempBan = ItemTimer.find_obv_of_item(self.banned_items, to_check.item)
            if temp_ban is None:
                print("pickup check -> item is still there -> failed to pick -> temp ban", to_check.item)
                self.banned_items.append(ItemTempBan(to_check.item))
                continue
            temp_ban.mark_retried()
        self.items_to_be_verified = new_queue

    def __check(self):
        latest_map = fetch_map_entities(self.api)
        me_now = fetch_player_info(self.api)
        if latest_map is None or me_now is None:
            return
        me_y, me_x = me_now['y'], me_now['x']

        def s(item: ItemEntity):
            return cal_distance((me_y, me_x), (item.y, item.x))

        # deal with old stuff
        self.__process_recently_picked_items_and_remove_from_list(latest_map)
        self.__add_ban_new_others_items(me_now, latest_map)

        # means to drop target
        # - it was recently picked up and waiting for check
        # - it was checked and marked as banned and wait for second chance
        # - item not on map anymore
        if self.target_item is not None:
            for i in range(1):
                if ItemTimer.find_obv_of_item(self.items_to_be_verified, self.target_item) is not None:
                    self.target_item = None
                    break

                temp_ban: ItemTempBan = ItemTimer.find_obv_of_item(self.banned_items, self.target_item)
                if temp_ban is not None:
                    if not temp_ban.ready_for_second_chance() or temp_ban.gave_up():
                        self.target_item = None
                        break

                if latest_map.find_item_with_id(self.target_item.id) is None:
                    self.target_item = None
                    break

        dist_target = None

        if self.target_item is None:
            top_candidate = self.__get_item_top_candidate(me_now, latest_map)
            self.target_item = top_candidate
            print('set target from candidate', top_candidate)

        if self.target_item is None:
            # no target and no candidate
            return

        if self.next_act_timer.allow_and_reset():
            if dist_target is None:
                dist_target = cal_distance((me_y, me_x), (self.target_item.y, self.target_item.x))

            dist_str = f'{dist_target:2f}'
            if dist_target > NostyQuickHandForeverLogic.PICK_DIST:
                # print(self.target_item.id, 'walk to item', dist_str)
                self.api.player_walk(self.target_item.x, self.target_item.y)
            else:
                print(self.target_item.id, 'picking item', dist_str)
                self.api.send_packet(f'get 1 {me_now["id"]} {self.target_item.id}')
                self.items_to_be_verified.append(ItemTimer(self.target_item, cooldown=2))

    def on_all_tick(self, json_msg: dict):
        if self.next_act_timer.allow_and_reset():
            self.__check()


class NostyExperimentLogic(twnz.bot.base.NostyEmptyLogic):

    def on_start_clicked(self):
        pass

    def on_recv(self, head: str, tail: str):
        pass