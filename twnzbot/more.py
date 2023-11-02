import twnzbot.base
from phoenixapi import phoenix
from twnzbot.enums import Mode
from twnzlib import fetch_current_y_x_map_id, image_to_binary_array, walk_to, find_intersection_xy


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
        # print('recv guri mode')
        print(head, tail)
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


class NostyExperimentLogic(twnzbot.base.NostyEmptyLogic):
    def get_mode(self):
        return Mode.EXPERIMENT

    def on_start(self):
        pass

    def on_recv(self, head: str, tail: str):
        pass
        # print('recv guri mode')
        # print(head, tail)
        # if head != 'hidn':
        #     return
        #
        # print("[RECV]:", head, tail)
        # _, deg, x, y = eval('('+','.join(tail.split()) + ')')
        # self.guri_points.append((y, x, deg))
        # print("*** hidn received, saving a marker yx", self.guri_points[-1])
        # print(self.guri_points)
        #
        # if len(self.guri_points) > 2:
        #     self.guri_points = self.guri_points[1:]
        # if len(self.guri_points) >= 2:
        #     cur_y, cur_x, map_id = fetch_current_y_x_map_id(self.api)
        #     map_array = image_to_binary_array(map_id)
        #     treasure_yx = find_intersection_xy(self.guri_points[0], self.guri_points[1], map_array.shape[0])
        #     print("*** intersection from last 2 cracks yx", treasure_yx)
        #     print("walking ")
        #     go_to_treasure(self.api, treasure_yx)
        #     self.guri_points = []
