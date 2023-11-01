import sys

from PyQt5.QtWidgets import QApplication

import root_config
from root_config import PB_URL
from pocketbase import PocketBase

import twnzlib.config
from twnzlib import *
from medals import *
import twnzui as ui
from twnzui import PortSelectionGUI
from twnzui.login_form import LoginResult

guri_points = []

def handle_send(packet: str):
    print("[SEND]: " + packet)


def handle_recv(api: phoenix.Api, packet: str):
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
            go_to_treasure(api, treasure_yx)
            guri_points = []
    else:
        # print('RECV', packet)
        pass


def go_to_treasure(api: phoenix.Api, treasure_point_yx):
    cur_y, cur_x, map_id = fetch_current_y_x_map_id(api)
    map_array = image_to_binary_array(map_id)
    print('go_to_treasure at', treasure_point_yx)
    walk_to(api, map_array, treasure_point_yx)


def run_login_block_and_exit_if_failed(app: QApplication) -> LoginResult:
    out = LoginResult()
    pb = PocketBase(root_config.PB_URL)
    login_ui = ui.LoginApplication(pb, out)
    login_ui.show()
    app.exec_()
    app.exit(0)
    if not out.success:
        exit(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_result = run_login_block_and_exit_if_failed(app)

    ports = returnAllPorts()
    port = []

    if len(ports) == 1:
        port = [int(ports[0][1])]
    else:
        port = []

    if not port:
        port_selection_app = PortSelectionGUI(ports, port)
        port_selection_app.show()
        print('exec')
        app.exec_()
        print('exiting')
        app.exit(0)
        print('exited')

    if not port:
        print('no port selected after port gui')
        exit(1)

    # port = input("enter port: ")
    api = phoenix.Api(int(port[0]))

    print('starting api')

    while api.working():
        occasional_log(api)

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
            sleep(twnzlib.config.API_INTERVAL)
    api.close()
