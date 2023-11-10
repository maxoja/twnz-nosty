import os
import sys
import atexit
import signal
import threading

from PyQt5.QtWidgets import QApplication, QAction

import twnz
from pocketbase import PocketBase

from twnz.bot.instances import NostyBotInstance
from twnz import *
from twnz import ui as ui
from twnz.ui.login_form import LoginResult
from twnz.ui.tray import NostyTray
from twnz.win.bridge import show_win_with_small_delay_if_not_already
from twnz.win.basic import get_window_of_handle, is_admin
from twnz.managers import SingletonLocker, on_any_signal_unlock, on_exit_unlock, NostyInstanceManager

break_main_loop = False

def run_login_block_and_keep_retry(app: QApplication):
    out = LoginResult()
    pb = PocketBase(root_config.PB_URL)
    login_ui = ui.LoginApplication(pb, out)
    login_ui.show()
    app.exec_()
    app.exit(0)
    if not out.success:
        sys.exit(0)

def show_exit_popup_and_exit_if_not_running_as_admin(app: QApplication):
    if not is_admin():
        s = "Please 'Run as Admin' in order to have Nosty UI and bots running stably"
        box = twnz.ui.misc.MessageBox(s)
        box.show()
        app.exec_()
        app.exit(0)
        sys.exit(0)

def start():
    signal.signal(signal.SIGINT, on_any_signal_unlock)
    signal.signal(signal.SIGTERM, on_any_signal_unlock)
    atexit.register(on_exit_unlock)

    app = QApplication(sys.argv)
    show_exit_popup_and_exit_if_not_running_as_admin(app)

    try:
        if SingletonLocker.is_locked_for_other_process():
            locked_by_pid = SingletonLocker.get_lock_content_pid()
            # kill those processes
            kill_process_tree(locked_by_pid)
            # box = twnz.ui.misc.MessageBox("Nosty Bot is already running in the background (" + str(locked_by_pid) + ")")
            # box.show()
            # app.exec_()
            # app.exit(0)
        elif SingletonLocker.is_locked_for_this_process():
            pass
        else:
            SingletonLocker.clear_lock_if_exist_and_lock()
    except Exception as e:
        s = "Nosty UI found issues when locking file" + "\n" + str(e)
        box = twnz.ui.misc.MessageBox(s)
        box.show()
        app.exec_()
        app.exit(0)
        sys.exit(0)

    # run_login_block_and_keep_retry(app)
    print('started tray thread')
    nim = NostyInstanceManager()

    def kill_them_all():
        global break_main_loop
        print('kill clicked')
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

        for n in more_nosties:
            n.ctrl_win.show()

        to_remove = []
        party_select_actions = []
        cb_map = dict()

        def wrap_select_player_cb(handle: int):
            return lambda: show_win_with_small_delay_if_not_already(get_window_of_handle(handle))

        for n in nim.instances:
            qact = QAction(n.bot_win.get_player_name(), None, checkable=False)
            qact.triggered.connect(wrap_select_player_cb(n.game_win.window_handle))
            party_select_actions.append(qact)

        # Standard processing and mark any dead instance
        for n in nim.instances:
            if not n.check_alive():
                to_remove.append(n)
                continue
            first_action = QAction("Phoenix", None, checkable=False)
            first_action.triggered.connect(wrap_select_player_cb(n.bot_win.window_handle))
            n.update([first_action] + party_select_actions)
            n.tick_entry()
            if n.should_be_removed:
                to_remove.append(n)
                continue

        nim.close_n_cleanup_instances(to_remove)
        app.processEvents()
    nim.close_all()
    SingletonLocker.unlock_for_itself()
    kill_process_tree(os.getpid())
    app.exit(0)
    sys.exit(0)
    # sys.exit(app.exec_())
