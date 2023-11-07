import os
import sys
from typing import Set, List, Optional, Tuple

import pywinctl
from pygetwindow import Win32Window

import twnz
from twnz import string_dist
from twnz.bot.instances import NostyBotInstance
from twnz.ui.instances import BotWinInstance, NosTaleWinInstance
from twnz.win.sread import Locator

from twnz.win.basic import process_active, get_game_windows, get_game_pid_from_bot_port, get_win_of_pid


class SingletonLocker:
    LOCK_FILE_NAME = "my_program.lock"
    is_locked = False

    @staticmethod
    def rm_lock_skip_if_not_there():
        if not SingletonLocker.file_is_there():
            return
        os.remove(SingletonLocker.LOCK_FILE_NAME)

    @staticmethod
    def file_is_there():
        if not os.path.exists(SingletonLocker.LOCK_FILE_NAME):
            return False
        if not os.path.isfile(SingletonLocker.LOCK_FILE_NAME):
            return False
        return True

    @staticmethod
    def get_lock_content_pid() -> Optional[str]:
        if not SingletonLocker.file_is_there():
            return None
        try:
            with open(SingletonLocker.LOCK_FILE_NAME, "r") as f:
                content = f.read()
                lock_pid = int(content)
                return lock_pid
        except:
            return None


    @staticmethod
    def is_locked_for_other_process():
        if not SingletonLocker.file_is_there():
            return False
        with open(SingletonLocker.LOCK_FILE_NAME, "r") as f:
            content = f.read()
            lock_pid = int(content)
            return process_active(lock_pid)

    @staticmethod
    def is_locked_for_this_process():
        if not SingletonLocker.file_is_there():
            return False
        with open(SingletonLocker.LOCK_FILE_NAME, "r") as f:
            content = f.read()
            lock_pid = int(content)
            return lock_pid == os.getpid()

    @staticmethod
    def clear_lock_if_exist_and_lock():
        SingletonLocker.rm_lock_skip_if_not_there()
        with open(SingletonLocker.LOCK_FILE_NAME, "x") as file:
            file.write(str(os.getpid()))
            SingletonLocker.is_locked_by_others = True

    @staticmethod
    def unlock_for_itself():
        if not SingletonLocker.is_locked_for_this_process():
            return
        if not SingletonLocker.file_is_there():
            return
        os.remove(SingletonLocker.LOCK_FILE_NAME)


def on_any_signal_unlock(signum, frame):
    # Handle the signal (e.g., clean up resources)
    SingletonLocker.unlock_for_itself()
    sys.exit(1)


def on_exit_unlock():
    # Handle program exit (e.g., clean up resources)
    SingletonLocker.unlock_for_itself()


class NostyInstanceManager:
    def __init__(self):
        self.pbot_checked_once: Set[BotWinInstance] = set()
        self.instances: List[NostyBotInstance] = []

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
        # return twnz.ui.windows.get_game_windows_with_name_level_port(
        #     handle_blacklist=current_game_handles)

    def __find_fground_game_win(self) -> Optional[Win32Window]:
        # TODO can be moved to win package
        try:
            fg_win = pywinctl.getActiveWindow()
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
        pbots_to_match = [p for p in self.pbot_checked_once if p not in matched_pbots and p.ready_to_match()]

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
            n.on_stop_nosty()
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
    game_win_info = twnz.ui.windows.get_game_windows_with_name_level_port([game_win])[0]
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
