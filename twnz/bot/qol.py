import time

import win32gui

from twnz.bot.base import NostyEmptyLogic
from twnz.bot.enums import Mode
from twnz.ui.instances import BotWinInstance
from twnz.win.all import show_and_move_win_to_middle
from twnz.win.bridge import show_win_with_small_delay_if_not_already
from twnz.win.basic import get_window_of_handle, get_foreground_win
from twnz.win.sread import Locator


class NostyPhoenixLogic(NostyEmptyLogic):
    def get_mode(self):
        return Mode.PHOENIX

    def on_prep_load(self):
        win_obj = get_window_of_handle(self.pbot_win.window_handle)
        old_win = get_foreground_win()
        old_left, old_top = win_obj.left, win_obj.top
        show_and_move_win_to_middle(win_obj)
        w, h = 120, 25
        l, t = 0, win_obj.height - h
        if Locator.STATE_RUNNING.find_local_rect_on_window(win_obj, (l,t,w,h)) is not None:
            self.states.running = True
            self.ctrl_win.start = True
            self.ctrl_win.rerender_start_button()
        else:
            pass
        win_obj.moveTo(old_left, old_top)
        show_win_with_small_delay_if_not_already(old_win)

    def on_start_external(self):
        pass

    def on_stop_external(self):
        pass

    def on_stop_clicked(self):
        self.api.stop_bot()

    def on_start_clicked(self):
        self.api.start_bot()
