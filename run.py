import random
import time

from phoenixapi import phoenix
from time import sleep, time
import json
from twnzlib import *


walk_cd_timer = -1
walk_cd_step = 0.8


def walk_step(api: phoenix.Api, y: int, x: int):
    global walk_cd_timer
    global walk_cd_step

    if time() < walk_cd_timer + walk_cd_step:
        sleep(walk_cd_timer+walk_cd_step - time())
    api.player_walk(x, y)
    walk_cd_timer = time() + walk_cd_step


def walk_nearby(api: phoenix.Api, map_array, current_npoint: tuple):
    ny, nx = current_npoint
    diagonals = [(ny + dy, nx + dx) for dx in [-2, 2] for dy in [-1, 1]]

    for y,x in diagonals:
        block_val = map_array[y][x]
        if block_val == 1:
            break

    if map_array[y][x] == 0:
        # TODO walk to somewhere specific
        # this is very unlikely
        # let's assume we always find a good place
        pass

    walk_step(api, x, y)


def walk_along_path(api: phoenix.Api, path_points: list):
    points = path_points[::]
    while len(points) > 0:
        next = points[0]
        points = points[1:]
        y, x = next
        y, x = x, y
        walk_step(api, y, x)


guri_points = []


def handle_send(packet: str):
    print("[SEND]: " + packet)


def fetch_player_pos(api: phoenix.Api):
    api.query_player_information()
    # at this point assume that api.working()
    while api.working():
        if not api.empty():
            msg = api.get_message()
            json_msg = json.loads(msg)

            if not json_msg["type"] == phoenix.Type.query_player_info.value:
                continue

            global player_current_pos
            global map_id
            packet = json_msg['player_info']
            player_current_pos = (packet['y'], packet['x'])
            player_current_pos = player_current_pos[::-1] # this is intentional
            map_id = packet['map_id']
            break
        else:
            sleep(0.01)


def handle_recv(api: phoenix.Api, packet: str):
    global guri_points
    head = packet.split()[0]

    if head == 'hidn':
        fetch_player_pos(api)
        map_array = image_to_binary_array(f"src/{map_id}.png")
        map_h, map_w = map_array.shape

        print("[RECV]: " + packet)
        _, deg, x, y = eval("(" + ",".join(packet.split()[1:]) + ")")
        guri_points.append((x, y, deg))
        print("*** hidn received, saving a marker", guri_points[-1])
        print(guri_points)

        if len(guri_points) > 2:
            guri_points = guri_points[1:]
        if len(guri_points) >= 2:
            treasure_point = find_intersection(guri_points[0], guri_points[1], map_w, map_h)
            print("*** intersection from last 2 cracks x y", treasure_point)
            go_to_treasure(api, map_array, treasure_point)
            guri_points = []
    else:
        # print('RECV', packet)
        pass

# (138, 124)
def go_to_treasure(api: phoenix.Api, map_array, treasure_point):
    path_points = find_walk_path(map_array, player_current_pos, treasure_point)
    path_points = simplify_path(path_points)
    walk_along_path(api, path_points)

if __name__ == "__main__":
    # Put the port from the bot title, it should look something like
    # [Lv 99.(+80) CharacterName] - Phoenix Bot:123123
    port = input("enter port: ")
    # host = "82.27.140.49"
    print('connecting to',port)
    api = phoenix.Api(int(port))
    points = []

    print('map array loaded')
    # path_points = find_walk_path(map_array, (), (50, 50))

    # Logs all the packets that are sent/received from the client
    while api.working():
        if random.randint(0,500) == 50:
            fetch_player_pos(api)
            print(player_current_pos)

        if not api.empty():
            msg = api.get_message()
            json_msg = json.loads(msg)

            if json_msg["type"] == phoenix.Type.packet_send.value:
                # handle_send(json_msg["packet"])
                pass
            elif json_msg["type"] == phoenix.Type.packet_recv.value:
                handle_recv(api, json_msg["packet"])
                pass
            else:
                # unhandled msg type
                pass
        else:
            sleep(0.01) 

    api.close()

map_info = None
player_current_pos = None
map_id = None
map_w = None
map_h = None