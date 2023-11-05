import phoenixapi.phoenix
from twnzbot.enums import Mode


class NostyStates:
    INITIAL_MODE = Mode.PHOENIX # need to update
    def __init__(self):
        self.mode = NostyStates.INITIAL_MODE
        self.running = False