import time

import win32gui

from twnz import string_dist
from twnz.bot.base import NostyEmptyLogic
from twnz.bot.enums import Mode
from twnz.win.all import show_and_move_win_to_middle, get_z_ordered_windows
from twnz.win.bridge import show_win_with_small_delay_if_not_already
from twnz.win.basic import get_window_of_handle, get_foreground_win
from twnz.win.const import BOT_STATUS_TEMP_PNG
from twnz.win.sread import Locator, capture_and_crop_window, ocr_bot_status_img_to_text


class NostyPhoenixLogic(NostyEmptyLogic):
    def get_mode(self):
        return Mode.PHOENIX

    def on_prep_load(self):
        window_handles_on_top_phoenix_z_ordered = get_z_ordered_windows()
        for i,wh in enumerate(window_handles_on_top_phoenix_z_ordered):
            if wh == self.pbot_win.window_handle:
                window_handles_on_top_phoenix_z_ordered = window_handles_on_top_phoenix_z_ordered[:i][::-1]
                break

        win_obj = get_window_of_handle(self.pbot_win.window_handle)
        old_left, old_top = win_obj.left, win_obj.top
        show_and_move_win_to_middle(win_obj)
        w, h = 120, 25
        l, t = 0, win_obj.height - h

        # crop that
        local_ltwh = (l, t, w, h)
        if local_ltwh is None:
            l, t, r, b = win32gui.GetWindowRect(win_obj.getHandle())
            l, t, w, h = 0, 0, r - l, b - t
        else:
            l, t, w, h = local_ltwh
        cropped = capture_and_crop_window(win_obj, l, t, w, h, save_now=True, target_path=BOT_STATUS_TEMP_PNG)
        if cropped is None:
            # assume we can't do anything with it
            return

        # send to ocr api
        cropped.save(BOT_STATUS_TEMP_PNG)

        # move bot win back to its old place
        win_obj.moveTo(old_left, old_top)

        for wh in window_handles_on_top_phoenix_z_ordered:
            ww = get_window_of_handle(wh)
            show_win_with_small_delay_if_not_already(ww)

        state_text = ocr_bot_status_img_to_text()

        # take it and compare str dist
        dist_stop = string_dist("State: Stopped", state_text)
        dist_idle = string_dist("State: Idle", state_text)
        dist_running = string_dist("State: Running", state_text)
        print("dist to stop   ", dist_stop)
        print("dist to idle   ", dist_idle)
        print("dist to running", dist_running)
        min_dist = min(dist_stop, dist_idle, dist_running)

        if min_dist == dist_running:
            self.states.running = True
            self.ctrl_win.start = True
            self.ctrl_win.rerender_start_button()


    def on_start_external(self):
        pass

    def on_stop_external(self):
        pass

    def on_stop_clicked(self):
        self.api.stop_bot()

    def on_start_clicked(self):
        self.api.start_bot()
