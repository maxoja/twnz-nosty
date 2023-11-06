from twnz.bot.base import NostyEmptyLogic
from twnz.bot.enums import Mode


class NostyPhoenixLogic(NostyEmptyLogic):
    def get_mode(self):
        return Mode.PHOENIX

    def on_start(self):
        self.api.start_bot()

    def on_stop(self):
        self.api.stop_bot()
