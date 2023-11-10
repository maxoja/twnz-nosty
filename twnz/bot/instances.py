import json
from typing import List

import win32gui
from PyQt5.QtWidgets import QAction
from win32ctypes.pywin32 import pywintypes

import twnz
import twnz.win.all
from twnz import phoenix
from twnz.bot import enums
from twnz.bot.enums import Mode, Feature
from twnz.bot.maps import feature_to_modes, mode_to_logic_class
from twnz.bot.models import NostyStates
from twnz.pb.models import FeatureModel
from twnz.ui.instances import NosTaleWinInstance, BotWinInstance
from twnz.ui.sticky import SmallWindow, update_small_windows_positions


def get_logic_for_mode(m: enums.Mode, api: phoenix.Api, states: NostyStates, ctrl_win: SmallWindow, pbot_win: BotWinInstance):
    logic_class = mode_to_logic_class(m)
    return logic_class(api, states, ctrl_win, pbot_win)


def features_to_modes(features: List[FeatureModel]) -> List[Mode]:
    result = []
    for f in features:
        f_enum = Feature(f.enum_name)
        modes = feature_to_modes(f_enum)
        result += [m for m in modes if m not in result]
    return result


class NostyBotInstance:
    def __init__(self, game_win: NosTaleWinInstance, bot_win: BotWinInstance, features: List[FeatureModel]):
        player_name = bot_win.get_player_name()
        self.ctrl_win = SmallWindow(player_name, features_to_modes(features), player_name=player_name)
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
        try:
            left, top, _, _ = self.game_win.get_rect()
            title = self.game_win.get_title()
            visible = twnz.win.all.is_window_partially_visible(self.game_win.window_handle)
            game_win_info = (left, top, title, visible)
            update_small_windows_positions([self.ctrl_win], [game_win_info], (110, 31))
            self.ctrl_win.set_party_selector(party_selector_actions)
        except pywintypes.error as e:
            print(e)
            self.should_be_removed = True
            return

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

        try:
            # SECTION: always on
            self.instance_level_tick(json_msg)

            if not self.states.running:
                return
            self.logic.on_tick(json_msg)
        except pywintypes.error as e:
            print(e)
            self.should_be_removed = True
            return
        except IndexError as e:
            # from get_player_level
            print(e)
            self.should_be_removed = True
            return
