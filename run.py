import sys
from typing import List

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


def run_login_block_and_exit_if_failed(app: QApplication):
    out = LoginResult()
    pb = PocketBase(root_config.PB_URL)
    login_ui = ui.LoginApplication(pb, out)
    login_ui.show()
    app.exec_()
    app.exit(0)
    if not out.success:
        exit(0)


def find_more_nosty_instances(current_nosties: List[NostyBotInstance]) -> List[NostyBotInstance]:
    bot_win_handles = [n.bot_win.window_handle for n in current_nosties]
    phoenix_wins = BotWinInstance.get_all(handle_blacklist=bot_win_handles)

    if len(phoenix_wins) == 0:
        return []

    game_win_handles = [n.game_win.window_handle for n in current_nosties]
    nostale_win_name_lv_ports = twnzui.windows.get_game_windows_with_name_level_port(handle_blacklist=game_win_handles)
    return match_eiei(phoenix_wins, nostale_win_name_lv_ports)


def create_nosty_instances() -> List[NostyBotInstance]:
    phoenix_wins = BotWinInstance.get_all()
    nostale_win_name_lv_ports = twnzui.windows.get_game_windows_with_name_level_port()
    return match_eiei(phoenix_wins, nostale_win_name_lv_ports)


def match_eiei(phoenix_wins, nostale_win_name_lv_ports):
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


def close_n_cleanup_instance(to_close: [NostyBotInstance], inst_list: List[NostyBotInstance]):
    for n in to_close:
        n.on_stop()
        n.ctrl_win.hide()
        n.api.close()
        inst_list.remove(n)


def keep_trying_if_empty(found_nosties: List[NostyBotInstance], prompt: bool=True):
    while len(found_nosties) == 0:
        if prompt:
            box = twnzui.misc.MessageBox(
                "Cannot find any of Phoenix Bot instances.\nMake sure Phoenix Bot is opened before running Nosty Bot")
            box.show()
            app.exec_()
            app.exit(0)
        else:
            sleep(0.1)
        found_nosties = create_nosty_instances()
    return found_nosties


if __name__ == "__main__":

    app = QApplication(sys.argv)
    run_login_block_and_exit_if_failed(app)

    nosties = create_nosty_instances()
    nosties = keep_trying_if_empty(nosties)

    for n in nosties:
        n.ctrl_win.show()

    while True:
        if len(nosties) == 0:
            break

        more_nosties = find_more_nosty_instances(nosties)
        for n in more_nosties:
            n.ctrl_win.show()
        nosties = nosties + more_nosties

        to_remove = []

        # Standard processing and mark any dead instance
        for n in nosties:
            if not n.check_alive():
                to_remove.append(n)
                continue
            n.update()
            n.bot_tick()

        # Close and cleanup dead instance
        close_n_cleanup_instance(to_remove, nosties)
        app.processEvents()
    app.exit(0)
    exit(0)
    # sys.exit(app.exec_())
