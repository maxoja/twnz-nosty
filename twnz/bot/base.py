from phoenixapi import phoenix
from twnz.bot.enums import Mode
from twnz.bot.models import NostyStates
from twnz.ui.instances import BotWinInstance
from twnz.ui.sticky import SmallWindow


class NostyEmptyLogic:
    def __init__(self, api: phoenix.Api, states: NostyStates, ctrl_win: SmallWindow, pbot_win: BotWinInstance):
        self.api = api
        self.states = states
        self.ctrl_win = ctrl_win
        self.pbot_win = pbot_win

    def get_mode(self):
        return Mode.NONE

    def on_prep_load(self):
        pass

    def on_load(self):
        pass

    def on_start_clicked(self):
        # when start button clicked
        pass

    def on_stop_clicked(self):
        # when stop button clicked
        pass

    def on_start_external(self):
        # when instance created or this logic mode was chosen
        # use clicked action by default
        # we don't really use this right now but will later
        # that's because when you start bot or switch mode, nosty won't automatically kick it off
        self.on_start_clicked()

    def on_stop_external(self):
        # when changed to different logic or nosty was killed
        # use clicked action by default
        self.on_stop_clicked()

    def on_tick(self, json_msg: dict):
        self.on_all_tick(json_msg)
        type_num = json_msg["type"]
        packet_str = json_msg["packet"] if "packet" in json_msg else None
        packet_head = packet_str.split(" ")[0] if packet_str is not None else None
        packet_tail = packet_str.replace(packet_head + " ", "", 1) if packet_head is not None else None

        if type_num == phoenix.Type.packet_send.value:
            self.on_send(packet_head, packet_tail)
        elif type_num == phoenix.Type.packet_recv.value:
            self.on_recv(packet_head, packet_tail)
        else:
            self.on_others(type_num, json_msg)

    def on_all_tick(self, json_msg: dict):
        pass

    def on_send(self, head: str, tail: str):
        pass

    def on_recv(self, head: str, tail: str):
        pass

    def on_others(self, type_num: int, json_msg: dict):
        pass
