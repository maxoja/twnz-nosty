import json
from typing import List

import win32gui
from PyQt5.QtWidgets import QAction

import twnz
import twnz.win.all
from phoenixapi import phoenix
from twnz.bot import enums, base, qol, more
from twnz.bot.enums import Mode
from twnz.bot.models import NostyStates
from twnz.ui.instances import NosTaleWinInstance, BotWinInstance
from twnz.ui.sticky import SmallWindow, update_small_windows_positions


def get_logic_for_mode(m: enums.Mode, api: phoenix.Api, states: NostyStates, ctrl_win: SmallWindow, pbot_win: BotWinInstance):
    if m == enums.Mode.NONE:
        return base.NostyEmptyLogic(api, states, ctrl_win, pbot_win)
    elif m == enums.Mode.PHOENIX:
        return qol.NostyPhoenixLogic(api, states, ctrl_win, pbot_win)
    elif m == enums.Mode.BROKEN_GURI:
        return more.NostyGuriLogic(api, states, ctrl_win, pbot_win)
    elif m == enums.Mode.PICK_ITEMS_ONESHOT:
        return more.NostyQuickHandLogic(api, states, ctrl_win, pbot_win)
    elif m == enums.Mode.PICK_ITEMS_FOREVER:
        return more.NostyQuickHandForeverLogic(api, states, ctrl_win, pbot_win)
    elif m == enums.Mode.EXPERIMENT:
        return more.NostyExperimentLogic(api, states, ctrl_win, pbot_win)
    else:
        raise Exception("Undefined map for mode " + m)


class NostyBotInstance:
    def __init__(self, game_win: NosTaleWinInstance, bot_win: BotWinInstance):
        player_name = bot_win.get_player_name()
        self.ctrl_win = SmallWindow(player_name, player_name=player_name)
        self.game_win = game_win
        self.bot_win = bot_win
        self.api = phoenix.Api(bot_win.get_port())
        self.states = NostyStates()
        self.bind_ctrl()
        self.load_logic__this_should_be_called_later(NostyStates.INITIAL_MODE)
        self.should_be_removed = False

    def bind_ctrl(self):
        self.ctrl_win.start_cb = self.on_start_clicked
        self.ctrl_win.stop_cb = self.on_stop_clicked
        self.ctrl_win.mode_cb = self.on_mode

    def on_start_nosty(self):
        self.states.running = True
        self.logic.on_start_external()

    def on_stop_nosty(self):
        self.states.running = False
        self.logic.on_stop_external()

    def on_start_clicked(self):
        self.states.running = True
        self.logic.on_start_clicked()

    def on_stop_clicked(self):
        self.states.running = False
        self.logic.on_stop_clicked()

    def render_stop_without_trigger(self):
        if self.ctrl_win.start:
            self.ctrl_win.on_start_clicked(True)

    def on_mode(self, selected_mode: Mode):
        prev_mode = self.states.mode
        self.states.mode = selected_mode
        if prev_mode != selected_mode:
            self.on_stop_clicked()
            self.render_stop_without_trigger()
            self.load_logic__this_should_be_called_later(selected_mode)

    def load_logic__this_should_be_called_later(self, mode:Mode):
        self.logic = get_logic_for_mode(mode, self.api, self.states, self.ctrl_win, self.bot_win)
        self.logic.on_prep_load()
        self.logic.on_load()

    def check_alive(self):
        if not self.bot_win.ready_to_match():
            return False
        try: win32gui.GetWindowRect(self.game_win.window_handle)
        except: return False
        try: win32gui.GetWindowRect(self.bot_win.window_handle)
        except: return False
        return True

    def update(self, party_selector_actions: List[QAction]):
        left, top, _, _ = self.game_win.get_rect()
        visible = twnz.win.all.is_window_partially_visible(self.game_win.window_handle)
        game_win_info = (left, top, self.game_win.get_title(), visible)
        update_small_windows_positions([self.ctrl_win], [game_win_info], (110, 31))
        self.ctrl_win.set_party_selector(party_selector_actions)

    def instance_level_tick(self, json_msg: dict):
        type_num = json_msg["type"]
        if type_num == phoenix.Type.packet_send.value:
            packet_str = json_msg["packet"]
            # print(packet_str)
            if packet_str is not None and "No" in packet_str and "NONE_CII" in packet_str:
                # print('mark for remove')
                self.should_be_removed = True
        if self.bot_win.get_player_level() == 0:
            self.should_be_removed = True

    def tick_entry(self):
        if not self.api.working():
            print("ERROR: api not working", self.bot_win.get_title())
            self.should_be_removed = True
            return

        # occasional_log(self.api, self.bot_win.get_player_name())

        if self.api.empty():
            return

        json_msg = json.loads(self.api.get_message())

        # SECTION: always on
        self.instance_level_tick(json_msg)

        if not self.states.running:
            return
        self.logic.on_tick(json_msg)
