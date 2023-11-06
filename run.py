import atexit
import signal
import sys
import threading

from PyQt5.QtWidgets import QApplication, QAction

import root_config
import twnz
from pocketbase import PocketBase

from twnz.bot.instances import NostyBotInstance
from twnz import *
from twnz import ui as ui
from twnz.ui.login_form import LoginResult
from twnz.ui.tray import NostyTray
from twnz.win.all import show_win_with_small_delay
from twnz.win.basic import get_window_of_handle
from twnz.managers import SingletonLocker, on_any_signal_unlock, on_exit_unlock, NostyInstanceManager


def run_login_block_and_exit_if_failed(app: QApplication):
    out = LoginResult()
    pb = PocketBase(root_config.PB_URL)
    login_ui = ui.LoginApplication(pb, out)
    login_ui.show()
    app.exec_()
    app.exit(0)
    if not out.success:
        exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, on_any_signal_unlock)
    signal.signal(signal.SIGTERM, on_any_signal_unlock)
    atexit.register(on_exit_unlock)

    app = QApplication(sys.argv)

    try:
        SingletonLocker.lock()
    except:
        box = twnz.ui.misc.MessageBox("Nosty Bot is already running in the background")
        box.show()
        app.exec_()
        app.exit(0)
        exit(0)

    # run_login_block_and_exit_if_failed(app)

    print('started tray thread')
    nim = NostyInstanceManager()

    break_main_loop = False
    def kill_them_all():
        global break_main_loop
        break_main_loop = True

    def thread_func():
        NostyTray(kill_them_all)

    tray_thread = threading.Thread(target=thread_func)
    tray_thread.daemon = True
    tray_thread.start()

    nim.create_all()

    for n in nim.instances:
        n.ctrl_win.show()

    while True:
        if break_main_loop:
            print('breaking main loop')
            break
        if len(nim.instances) == 0:
            sleep(1)

        more_nosties = nim.find_n_try_match_new_pbot_wins_update_return()
        if len(more_nosties) == 0:
            new_nosty = nim.find_active_game_and_try_match_with_leftover_pbot_update_n_return()
            if new_nosty is not None:
                more_nosties = [new_nosty]

        for n in more_nosties:
            n.ctrl_win.show()

        to_remove = []

        party_select_actions = []
        cb_map = dict()

        def wrap_select_player_cb(nosty: NostyBotInstance):
            return lambda: show_win_with_small_delay(get_window_of_handle(nosty.game_win.window_handle))

        for n in nim.instances:
            qact = QAction(n.bot_win.get_player_name(), n.ctrl_win, checkable=False)
            qact.triggered.connect(wrap_select_player_cb(n))
            party_select_actions.append(qact)

        # Standard processing and mark any dead instance
        for n in nim.instances:
            if not n.check_alive():
                to_remove.append(n)
                continue
            n.update(party_select_actions)
            n.tick_entry()
            if n.should_be_removed:
                to_remove.append(n)
                continue

        nim.close_n_cleanup_instances(to_remove)
        app.processEvents()
    nim.close_all()
    app.exit(0)
    sys.exit(0)
    # sys.exit(app.exec_())
