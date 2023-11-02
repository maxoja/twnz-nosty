from phoenixapi import phoenix
from twnzbot.enums import Mode
from twnzbot.models import NostyStates


class NostyEmptyLogic:
    def __init__(self, api: phoenix.Api, states: NostyStates):
        self.api = api
        self.states = states

    def get_mode(self):
        return Mode.NONE

    def on_start(self):
        pass

    def on_stop(self):
        pass

    def on_tick(self, json_msg: dict):
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

    def on_send(self, head: str, tail: str):
        pass

    def on_recv(self, head: str, tail: str):
        pass

    def on_others(self, type_num: int, json_msg: dict):
        pass
