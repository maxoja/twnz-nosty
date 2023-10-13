from time import time, sleep

import numpy as np

from phoenixapi import phoenix
from twnzlib import find_walk_path_pruned, fetch_current_y_x_map_id, config


class WalkStates:
    def __init__(self, next_step_time: float = -1):
        self.next_walk_time = next_step_time


def walk_step(api: phoenix.Api, y: int, x: int, states: WalkStates):
    if time() < states.next_walk_time + config.WALK_CHECK_INTERVAL:
        sleep(states.next_walk_time + config.WALK_CHECK_INTERVAL - time())
    print('walking to', y, x)
    api.player_walk(x, y)
    states.next_walk_time = time() + config.WALK_CHECK_INTERVAL


def walk_nearby(api: phoenix.Api, map_array: np.ndarray, current_npoint: tuple):
    ny, nx = current_npoint
    diagonals = [(ny + dy, nx + dx) for dx in [-2, 2] for dy in [-1, 1]]

    for y, x in diagonals:
        block_val = map_array[y][x]
        if block_val == 1:
            break

    if map_array[y][x] == 0:
        # TODO walk to somewhere specific
        # this is very unlikely
        # let's assume we always find a good place
        pass
    walk_step(api, x, y)


def walk_along_path(api: phoenix.Api, path_points: list, states: WalkStates):
    points = path_points[::]
    while len(points) > 0:
        next = points[0]
        points = points[1:]
        y, x = next
        walk_step(api, y, x, states)

        cur_y, cur_x, _ = fetch_current_y_x_map_id(api)
        while (cur_y, cur_x) != (y, x):
            sleep(0.01)
            cur_y, cur_x, _ = fetch_current_y_x_map_id(api)


def walk_to(api: phoenix.Api, map_array: np.ndarray, dest_yx: tuple, states: WalkStates):
    print('walk to', dest_yx)
    cur_y, cur_x, _ = fetch_current_y_x_map_id(api)
    path_points = find_walk_path_pruned(map_array, (cur_y, cur_x), dest_yx)
    walk_along_path(api, path_points, states)
