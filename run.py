import twnzlib.config
from twnzlib import *

guri_points = []


def handle_send(packet: str):
    print("[SEND]: " + packet)


def handle_recv(api: phoenix.Api, packet: str, states: WalkStates):
    global guri_points
    head = packet.split()[0]

    if head == 'hidn':
        print("[RECV]: " + packet)

        _, deg, x, y = eval("(" + ",".join(packet.split()[1:]) + ")")
        guri_points.append((y, x, deg))
        print("*** hidn received, saving a marker yx", guri_points[-1])
        print(guri_points)

        if len(guri_points) > 2:
            guri_points = guri_points[1:]
        if len(guri_points) >= 2:
            cur_y, cur_x, map_id = fetch_current_y_x_map_id(api)
            map_array = image_to_binary_array(map_id)
            treasure_yx = find_intersection_xy(guri_points[0], guri_points[1], map_array.shape[0])
            print("*** intersection from last 2 cracks yx", treasure_yx)
            print("walking ")
            go_to_treasure(api, treasure_yx, states)
            guri_points = []
    else:
        # print('RECV', packet)
        pass


def go_to_treasure(api: phoenix.Api, treasure_point_yx, states: WalkStates):
    cur_y, cur_x, map_id = fetch_current_y_x_map_id(api)
    map_array = image_to_binary_array(map_id)
    print('go_to_treasure at', treasure_point_yx)
    walk_to(api, map_array, treasure_point_yx, states)


if __name__ == "__main__":
    port = input("enter port: ")
    api = phoenix.Api(int(port))
    walk_states = WalkStates()
    points = []

    while api.working():
        occasional_log(api)

        if not api.empty():
            msg = api.get_message()
            json_msg = json.loads(msg)

            if json_msg["type"] == phoenix.Type.packet_send.value:
                # handle_send(json_msg["packet"])
                pass
            elif json_msg["type"] == phoenix.Type.packet_recv.value:
                handle_recv(api, json_msg["packet"], walk_states)
                pass
            else:
                # unhandled msg type
                pass
        else:
            sleep(twnzlib.config.API_INTERVAL)
    api.close()
