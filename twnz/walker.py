from time import time, sleep

import numpy as np

from phoenixapi import phoenix
from twnz import find_walk_path_pruned, fetch_current_y_x_map_id, config

def walk_nearby(api: phoenix.Api, map_array: np.ndarray, current_npoint: tuple):
    # TODO
    return
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


def walk_to(api: phoenix.Api, map_array: np.ndarray, dest_yx: tuple):
    print('walk to', dest_yx)
    cur_y, cur_x, _ = fetch_current_y_x_map_id(api)
    dest_x, dest_y = dest_yx[::-1]
    print('sending walk')
    api.player_walk(dest_x, dest_y)
    print('finish sending walk')
    # path_points = find_walk_path_pruned(map_array, (cur_y, cur_x), dest_yx)
    # walk_along_path(api, path_points, states)
