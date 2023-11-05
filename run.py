import atexit
import os
import signal
import sys
from typing import List, Set, Optional, Tuple
import threading

import psutil
from PyQt5.QtWidgets import QApplication
from pygetwindow import Win32Window

import root_config
import twnzui.windows
from pocketbase import PocketBase

from twnzbot.instances import NostyBotInstance
from twnzlib import *
import twnzui as ui
from twnzui.instances import NosTaleWinInstance, BotWinInstance
from twnzui.login_form import LoginResult
from twnzui.tray import NostyTray
from twnzui.windows import Locator


def run_login_block_and_exit_if_failed(app: QApplication):
    out = LoginResult()
    pb = PocketBase(root_config.PB_URL)
    login_ui = ui.LoginApplication(pb, out)
    login_ui.show()
    app.exec_()
    app.exit(0)
    if not out.success:
        exit(0)


def process_active(pid: int or str) -> bool:
    try:
        process = psutil.Process(pid)
    except psutil.Error as error:  # includes NoSuchProcess error
        return False
    if psutil.pid_exists(pid) and process.status() == psutil.STATUS_RUNNING:
        return True


class NostyInstanceManager:
    def __init__(self):
        self.pbot_checked_once: Set[BotWinInstance] = set()
        self.instances: List[NostyBotInstance] = []

    @staticmethod
    def lock():
        try:
            global locked
            file = open(lock_file, "x")
            file.write(str(os.getpid()))
            locked = True
        except FileExistsError:
            with open(lock_file, "r") as f:
                content = f.read()
                lock_pid = int(content)

            if lock_pid == os.getpid():
                print('redundant lock file, considered already correctly locked')
                locked = True
                return

            if not process_active(lock_pid):
                print('expired lock file, remove lock and relock')
                os.remove(lock_file)
                locked = False
                NostyInstanceManager.lock()
                return
            print("Another instance of the program is already running.")
            sys.exit(1)

    @staticmethod
    def unlock():
        if locked and os.path.exists(lock_file) and os.path.isfile(lock_file):
            os.remove(lock_file)


    def create_all(self):
        # find all nostale wins if start first time
        phoenix_wins = BotWinInstance.get_all()
        self.pbot_checked_once.update(phoenix_wins)
        ready_phoenix_wins = [p for p in phoenix_wins if p.ready_to_match()]
        self.instances = match_v3(ready_phoenix_wins)

    def __get_matched_pbots(self):
        return [i.bot_win for i in self.instances]

    def __find_new_pbot_wins(self):
        # pbot that's not matched and not checked
        bot_win_handles = [p.window_handle for p in self.pbot_checked_once]
        return BotWinInstance.get_all(handle_blacklist=bot_win_handles)

    def __find_unmatched_game_wins(self) -> List[Win32Window]:
        current_game_handles = [n.game_win.window_handle for n in self.instances]
        return get_game_windows(current_game_handles)
        # return twnzui.windows.get_game_windows_with_name_level_port(
        #     handle_blacklist=current_game_handles)

    def __find_fground_game_win(self) -> Optional[Win32Window]:
        try:
            fg_win = pwc.getActiveWindow()
            if "NosTale - (" in fg_win.title:
                return fg_win
            return None
        except:
            return None

    def find_n_try_match_new_pbot_wins_update_return(self) -> List[NostyBotInstance]:
        # new phoenix_box started, fidn matching nostale win
        new_pbots = self.__find_new_pbot_wins()
        if len(new_pbots) == 0:
            return []
        self.pbot_checked_once.update(new_pbots)
        new_matches = match_v3(new_pbots)
        self.instances.extend(new_matches)
        return new_matches

    def find_active_game_and_try_match_with_leftover_pbot_update_n_return(self) -> Optional[NostyBotInstance]:
        # for left-over phoenix bot that can't initially matched with nostale win
        # try to rematch it with unmateched nostale win that's currently active
        matched_pbots = self.__get_matched_pbots()
        pbots_to_match = [p for p in self.pbot_checked_once if p not in matched_pbots]

        if len(pbots_to_match) == 0:
            return None

        foreground_game_win = self.__find_fground_game_win()

        if foreground_game_win is None:
            return None
        matched_game_win_handles = [i.game_win.window_handle for i in self.instances]
        if foreground_game_win.getHandle() in matched_game_win_handles:
            return None
        if not game_win_matchable(foreground_game_win):
            return None

        # we now have unmatched pbot with active game that's matchable and not yet matched
        best_pbot_ins = find_best_pbot_win_for_game_win(foreground_game_win, pbots_to_match)
        fg_game_ins = NosTaleWinInstance(foreground_game_win.getHandle())
        new_nosty = NostyBotInstance(fg_game_ins, best_pbot_ins)
        self.instances.append(new_nosty)
        return new_nosty

    def close_n_cleanup_instances(self, to_close: [NostyBotInstance]):
        # TODO remove dead pbot instance from pbot_checked_once, bc it's possible for window handle could get reused
        for n in to_close[::]:
            n.on_stop()
            n.ctrl_win.hide()
            n.api.close()
            self.pbot_checked_once.remove(n.bot_win)
            self.instances.remove(n)

    def close_all(self):
        self.close_n_cleanup_instances(self.instances)


def game_win_matchable(w: Win32Window):
    rect = Locator.AVATAR_BALL.find_local_rect_on_window(w)
    if rect is not None: return True
    rect = Locator.MP_LABEL.find_local_rect_on_window(w)
    if rect is not None: return True
    rect = Locator.MAP_BUTTON.find_local_rect_on_window(w)
    # intentionally don't try to locate Locator.NOSTALE_TITLE
    # because it will also be there in server selection screen
    return rect is not None


def distance_pbot_game_info(pbot: BotWinInstance, nost_tuple: Tuple) -> int:
    n_name = nost_tuple[1]
    n_lv_sr = nost_tuple[2]
    name_dist = string_dist(n_name, pbot.get_player_name())
    lvl_dist = string_dist(n_lv_sr, str(pbot.get_player_level()))
    return name_dist + lvl_dist

def distance_pbot_game_info_wrap_pbot(pbot: BotWinInstance):
    # TODO would pbot get frozen as expected?
    return lambda n_tuple: distance_pbot_game_info(pbot, n_tuple)

def distance_pbot_game_info_wrap_nost_tuple(nost_tuple: Tuple):
    # TODO would game_info get frozen as expected?
    return lambda pbot: distance_pbot_game_info(pbot, nost_tuple)


def find_best_game_win_for_pbot_remove_inplace(p:BotWinInstance, game_win_info: List[Tuple]) -> NosTaleWinInstance:
    # game_win must not be None nor empty
    # pbots must not be None nor empty
    game_win_info.sort(key=distance_pbot_game_info_wrap_pbot(p), reverse=True)
    return NosTaleWinInstance(game_win_info.pop()[0].getHandle())


def find_best_pbot_win_for_game_win(game_win: Win32Window, pbots: List[BotWinInstance]) -> BotWinInstance:
    # game_win must not be None nor empty
    # pbots must not be None nor empty
    game_win_info = twnzui.windows.get_game_windows_with_name_level_port([game_win])[0]
    pbots.sort(key=distance_pbot_game_info_wrap_nost_tuple(game_win_info), reverse=True)
    return pbots[0]


def match_v3(phoenix_wins: List[BotWinInstance]) -> List[NostyBotInstance]:
    if len(phoenix_wins) == 0:
        return []
    result = []
    for p in phoenix_wins:
        game_pid = get_game_pid_from_bot_port(p.get_port())
        game_win = get_win_of_pid(game_pid)
        if game_win is None:
            continue
        game_ins = NosTaleWinInstance(game_win.getHandle())
        result.append(NostyBotInstance(game_ins, p))
    return result


def keep_trying_if_empty_and_prompt_ok(nim: NostyInstanceManager, prompt: bool=True):
    while len(nim.instances) == 0:
        if prompt:
            box = twnzui.misc.MessageBox(
                "Cannot find any of Phoenix Bot instances.\nMake sure Phoenix Bot is opened before running Nosty Bot", "Retry")
            box.show()
            app.exec_()
            app.exit(0)
        else:
            sleep(0.1)
        nim.create_all()


lock_file = "my_program.lock"
locked = False


def signal_handler(signum, frame):
    # Handle the signal (e.g., clean up resources)
    NostyInstanceManager.unlock()
    sys.exit(1)

def exit_handler():
    # Handle program exit (e.g., clean up resources)
    NostyInstanceManager.unlock()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(exit_handler)

    app = QApplication(sys.argv)

    try:
        NostyInstanceManager.lock()
    except:
        box = twnzui.misc.MessageBox("Nosty Bot is already running in the background")
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
    # keep_trying_if_empty_and_prompt_ok(nim)

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

        # Standard processing and mark any dead instance
        for n in nim.instances:
            if not n.check_alive():
                to_remove.append(n)
                continue
            n.update()
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
