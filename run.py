from phoenixapi import phoenix
from time import sleep
import json
from twnzlib import *


def walk_nearby(map_array, current_npoint: tuple):
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

    # TODO walk to y/x


def use_guriguri():
    # TODO
    pass


guri_points = []


def handle_send(packet):
    print("[SEND]: " + packet)


def handle_recv(packet: str):
    global guri_points
    packet = json_msg['packet']
    head = packet.split()[0]

    if head == 'hidn':
        print("[RECV]: " + json_msg["packet"])
        _, deg, x, y = eval("(" + ",".join(packet.split()[1:]) + ")")
        guri_points.append((x, y, deg))
        print("*** hidn received, saving a marker", guri_points[-1])
        if len(guri_points) > 2:
            guri_points = guri_points[1:]
        if len(points) >= 2:
            s = str(find_intersection(points[0], points[1], 90, 90))
            print("*** intersection from last 2 cracks", s)
    else:
        pass


if __name__ == "__main__":
    # Put the port from the bot title, it should look something like
    # [Lv 99.(+80) CharacterName] - Phoenix Bot:123123
    port = 4772
    # host = "82.27.140.49"
    # api = phoenix.Api(port)
    print(ndeg_to_rdeg(1.2))
    print("done")
    exit(0)
    points = []

    # Logs all the packets that are sent/received from the client
    while api.working():
        if not api.empty():
            msg = api.get_message()
            json_msg = json.loads(msg)

            if json_msg["type"] == phoenix.Type.packet_send.value:
                handle_send(json_msg["packet"])
            elif json_msg["type"] == phoenix.Type.packet_recv.value:
                handle_recv(json_msg["packet"])
        else:
            sleep(0.01) 

    api.close()