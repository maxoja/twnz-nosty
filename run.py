import sys
from typing import List, Set, Optional, Tuple

import win32gui
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


class NostyInstanceManager:
    def __init__(self):
        self.pbot_checked_once: Set[BotWinInstance] = set()
        self.instances: List[NostyBotInstance] = []

    def create_all(self):
        # find all nostale wins if start first time
        phoenix_wins = BotWinInstance.get_all()
        game_wins = get_game_windows()
        self.pbot_checked_once.update(phoenix_wins)
        self.instances = match_phoenix_n_nostale_wins(phoenix_wins, game_wins)

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
        except:
            return None
        finally:
            return None

    def find_n_try_match_new_pbot_wins_update_return(self) -> List[NostyBotInstance]:
        # new phoenix_box started, fidn matching nostale win
        new_pbots = self.__find_new_pbot_wins()
        unmatched_game = self.__find_unmatched_game_wins()
        self.pbot_checked_once.update(new_pbots)
        new_matches = match_phoenix_n_nostale_wins(new_pbots, unmatched_game)
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
        return NostyBotInstance(fg_game_ins, best_pbot_ins)

    def close_n_cleanup_instance(self, to_close: [NostyBotInstance]):
        # TODO remove dead pbot instance from pbot_checked_once, bc it's possible for window handle could get reused
        for n in to_close:
            n.on_stop()
            n.ctrl_win.hide()
            n.api.close()
            self.pbot_checked_once.remove(n.bot_win)
            self.instances.remove(n)


def find_more_nosty_instances(current_nosties: List[NostyBotInstance]) -> List[NostyBotInstance]:
    bot_win_handles = [n.bot_win.window_handle for n in current_nosties]
    phoenix_wins = BotWinInstance.get_all(handle_blacklist=bot_win_handles)

    if len(phoenix_wins) == 0:
        return []

    game_win_handles = [n.game_win.window_handle for n in current_nosties]
    game_wins_filtered = get_game_windows(handle_blacklist=game_win_handles)
    return match_phoenix_n_nostale_wins(phoenix_wins, game_wins_filtered)


def create_nosty_instances() -> List[NostyBotInstance]:
    phoenix_wins = BotWinInstance.get_all()
    game_wins = get_game_windows()
    return match_phoenix_n_nostale_wins(phoenix_wins, game_wins)


def game_win_matchable(w: Win32Window):
    rect = Locator.AVATAR_BALL.find_local_rect_on_window(w)
    if rect is not None: return True
    rect = Locator.MP_LABEL.find_local_rect_on_window(w)
    if rect is not None: return True
    rect = Locator.MAP_BUTTON.find_local_rect_on_window(w)
    if rect is not None: return True
    rect = Locator.NOSTALE_TITLE.find_local_rect_on_window(w)
    return rect is not None


def distance_pbot_game_info(pbot: BotWinInstance, nost_tuple: Tuple) -> int:
    n_name = nost_tuple[1]
    n_lv = nost_tuple[2]
    return string_dist(n_name, pbot.get_player_name()) + (1 if n_lv != pbot.get_player_level() else 0)

def distance_pbot_game_info_wrap_pbot(pbot: BotWinInstance):
    # TODO would pbot get frozen as expected?
    return lambda n_tuple: distance_pbot_game_info(pbot, n_tuple)

def distance_pbot_game_info_wrap_nost_tuple(nost_tuple: Tuple):
    # TODO would game_info get frozen as expected?
    return lambda pbot: distance_pbot_game_info(pbot, nost_tuple)

# Note -> it's ok to not have perfect match - we can just have UI to allow manual match later

def find_best_game_win_for_pbot_remove_inplace(p:BotWinInstance, game_win_info: List[Tuple]) -> NosTaleWinInstance:
    # TODO this assumes there will always be a match but that's not always the case
    # how to know when that's the case -> the win wouldn't be matchable?
    # what to do when we know that?
    # can we assume at this point that all given wins are matchable?
    game_win_info.sort(key=distance_pbot_game_info_wrap_pbot(p), reverse=True)
    return NosTaleWinInstance(game_win_info.pop()[0].getHandle())

def find_best_pbot_win_for_game_win(game_win: Win32Window, pbots: List[BotWinInstance]) -> BotWinInstance:
    game_win_info = twnzui.windows.get_game_windows_with_name_level_port([game_win])[0]
    pbots.sort(key=distance_pbot_game_info_wrap_nost_tuple(game_win_info), reverse=True)
    return pbots[0]


def match_phoenix_n_nostale_wins(phoenix_wins: List[BotWinInstance], game_wins: List[Win32Window]) -> List[NostyBotInstance]:
    # print('before check', len(game_wins))
    game_wins = [g for g in game_wins if game_win_matchable(g)]
    # print('after check', len(game_wins))
    game_wins_info = twnzui.windows.get_game_windows_with_name_level_port(game_wins)
    # print('game, game_info, pbot')
    # print(len(game_wins) , len(game_wins_info), len(phoenix_wins))

    pairs = []
    for p in phoenix_wins:
        best_game_win = find_best_game_win_for_pbot_remove_inplace(p, game_wins_info)
        pairs.append((p, best_game_win))

    result = []
    for p in pairs:
        phoenix_ins, nostale_ins = p
        result.append(NostyBotInstance(nostale_ins, phoenix_ins))

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


if __name__ == "__main__":

    app = QApplication(sys.argv)
    # run_login_block_and_exit_if_failed(app)

    nim = NostyInstanceManager()
    nim.create_all()
    keep_trying_if_empty_and_prompt_ok(nim)

    for n in nim.instances:
        n.ctrl_win.show()

    while True:
        if len(nim.instances) == 0:
            break

        more_nosties = nim.find_n_try_match_new_pbot_wins_update_return()
        for n in more_nosties:
            n.ctrl_win.show()

        to_remove = []

        # Standard processing and mark any dead instance
        for n in nim.instances:
            if not n.check_alive():
                to_remove.append(n)
                continue
            n.update()
            n.bot_tick()

        # Close and cleanup dead instance
        nim.close_n_cleanup_instance(to_remove)
        # close_n_cleanup_instance(to_remove, nim.instances)
        app.processEvents()
    app.exit(0)
    exit(0)
    # sys.exit(app.exec_())
