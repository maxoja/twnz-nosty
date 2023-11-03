import sys
from PyQt5.QtWidgets import QApplication

import root_config
import twnzui.windows
from pocketbase import PocketBase

from twnzbot.instances import NostyBotInstance
from twnzlib import *
import twnzui as ui
from twnzui.instances import NosTaleWinInstance, BotWinInstance
from twnzui.login_form import LoginResult

from twnzui.sticky import SmallWindow

guri_points = []

def handle_send(packet: str):
    print("[SEND]: " + packet)

def run_login_block_and_exit_if_failed(app: QApplication):
    out = LoginResult()
    pb = PocketBase(root_config.PB_URL)
    login_ui = ui.LoginApplication(pb, out)
    login_ui.show()
    app.exec_()
    app.exit(0)
    if not out.success:
        exit(0)


def create_nosty_instances():
    phoenix_wins = BotWinInstance.get_all()
    nostale_win_name_lv_ports = twnzui.windows.get_game_windows_with_name_level_port()

    pairs = []
    for p in phoenix_wins:
        p_name = p.get_player_name()
        p_lv = p.get_player_level()

        def sorting(nost_tuple):
            n_name = nost_tuple[1]
            n_lv = nost_tuple[2]
            return string_dist(n_name, p_name) + (1 if n_lv != p_lv else 0)

        sorted_win = sorted(nostale_win_name_lv_ports, key=sorting, reverse=True)
        pairs.append((p, NosTaleWinInstance(sorted_win.pop()[0].getHandle())))

    result = []
    for p in pairs:
        phoenix_ins, nostale_ins = p
        player_name = phoenix_ins.get_player_name()
        control_win = SmallWindow(player_name, player_name=player_name)
        api = phoenix.Api(phoenix_ins.get_port())
        result.append(NostyBotInstance(control_win, nostale_ins, phoenix_ins, api))

    return result


if __name__ == "__main__":
    app = QApplication(sys.argv)
    run_login_block_and_exit_if_failed(app)

    nosties = create_nosty_instances()

    while len(nosties) == 0:
        box = twnzui.misc.MessageBox("Cannot find any of Phoenix Bot instances.\nMake sure Phoenix Bot is opened before running Nosty Bot")
        box.show()
        app.exec_()
        app.exit(0)
        nosties = create_nosty_instances()

    for n in nosties:
        n.ctrl_win.show()

    while True:
        for n in nosties:
            n.update()
            n.bot_tick()
        app.processEvents()

    sys.exit(app.exec_())
