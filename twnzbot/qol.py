from phoenixapi import phoenix
from twnzbot.base import NostyEmptyLogic
from twnzbot.enums import Mode
from twnzbot.models import NostyStates
from twnzui.sticky import SmallWindow


class NostyPhoenixLogic(NostyEmptyLogic):
    def get_mode(self):
        return Mode.PHOENIX

    def on_start(self):
        self.api.start_bot()

    def on_stop(self):
        self.api.stop_bot()
