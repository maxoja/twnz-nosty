import json

import win32gui

import twnzui
from phoenixapi import phoenix
from twnzbot import enums, base, more
from twnzbot.enums import Mode
from twnzbot.models import NostyStates
from twnzui.instances import NosTaleWinInstance, BotWinInstance
from twnzui.sticky import SmallWindow, update_small_windows_positions


def get_logic_for_mode(m: enums.Mode, api: phoenix.Api, states: NostyStates):
    if m == enums.Mode.NONE:
        return base.NostyEmptyLogic(api, states)
    elif m == enums.Mode.BROKEN_GURI:
        return more.NostyGuriLogic(api, states)
    elif m == enums.Mode.EXPERIMENT:
        return more.NostyExperimentLogic(api, states)
    else:
        raise Exception("Undefined map for mode " + m)


class NostyBotInstance:
    def __init__(self, control_win: SmallWindow, game_win: NosTaleWinInstance, bot_win: BotWinInstance, api: phoenix.Api):
        self.ctrl_win = control_win
        self.game_win = game_win
        self.bot_win = bot_win
        self.api = api
        self.states = NostyStates()
        self.bind_ctrl()
        # assume states.mode is initially Mode.NONE
        self.logic = get_logic_for_mode(Mode.NONE, api, self.states)

    def bind_ctrl(self):
        self.ctrl_win.start_cb = self.on_start
        self.ctrl_win.stop_cb = self.on_stop
        self.ctrl_win.mode_cb = self.on_mode

    def on_start(self):
        self.states.running = True
        self.logic.on_start()

    def on_stop(self):
        self.states.running = False
        self.logic.on_stop()

    def render_stop_without_trigger(self):
        if self.ctrl_win.start:
            self.ctrl_win.on_start_clicked(True)

    def on_mode(self, selected_mode: Mode):
        prev_mode = self.states.mode
        self.states.mode = selected_mode
        if prev_mode != selected_mode:
            self.on_stop()
            self.render_stop_without_trigger()
            self.load_logic(selected_mode)

    def load_logic(self, mode:Mode):
        self.logic = get_logic_for_mode(mode, self.api, self.states)

    def check_alive(self):
        try: win32gui.GetWindowRect(self.game_win.window_handle)
        except: return False
        try: win32gui.GetWindowRect(self.bot_win.window_handle)
        except: return False
        return True

    def update(self):
        left, top, _, _ = self.game_win.get_rect()
        visible = twnzui.utils.is_window_partially_visible(self.game_win.window_handle)
        game_win_info = (left, top, self.game_win.get_title(), visible)
        update_small_windows_positions([self.ctrl_win], [game_win_info], (110, 31))

    def bot_tick(self):
        if not self.api.working():
            print("ERROR: api not working", self.bot_win.get_title())
            return

        # occasional_log(self.api, self.bot_win.get_player_name())

        if self.api.empty():
            return

        json_msg = json.loads(self.api.get_message())

        # SECTION: always on
        # do something here

        if not self.states.running:
            return
        self.logic.on_tick(json_msg)