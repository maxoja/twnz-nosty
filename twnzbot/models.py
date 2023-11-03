import phoenixapi.phoenix
from twnzbot.enums import Mode


class NostyStates:
    def __init__(self):
        self.mode = Mode.NONE
        self.running = False