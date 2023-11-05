from typing import List, Optional

import win32gui

from twnzlib import get_phoenix_windows


class BotWinInstance:
    def __init__(self, wh: int):
        self.window_handle = wh
        pass

    def get_title(self):
        return win32gui.GetWindowText(self.window_handle)

    def get_player_name(self):
        title = self.get_title()
        title = title.split("]")[0]
        title = title.split(" ")[-1]
        return title

    def get_player_level(self):
        title = self.get_title()
        return int(title.split(" ")[1].split("(")[0])

    def get_champ_level(self):
        title = self.get_title()
        if "(+" not in title:
            return 0
        return int(title.split("(+")[1].split(")")[0])

    def get_port(self) -> int:
        return int(self.get_title().split(":")[-1])

    @staticmethod
    def get_all(handle_blacklist: Optional[List[int]] = None):
        windows = get_phoenix_windows()
        handle_blacklist = [] if handle_blacklist is None else handle_blacklist
        return [BotWinInstance(w.getHandle()) for w in windows if w.getHandle() not in handle_blacklist]

    def __eq__(self, other):
        # assume other is of the same type
        return self.window_handle == other.window_handle

    def __hash__(self):
        # assume other is of the same type
        return self.window_handle


class NosTaleWinInstance:
    def __init__(self, wh: int):
        self.window_handle = wh
        pass

    def get_title(self):
        return win32gui.GetWindowText(self.window_handle)

    def get_port(self):
        title = self.get_title()
        title = title.split(" - (")[-1]
        return int(title.replace(")", ""))

    def get_rect(self):
        rect = win32gui.GetWindowRect(self.window_handle)
        return rect

    def get_left_top(self):
        return self.get_rect()[:2]

    def get_width_height(self):
        return self.get_rect()[2:]

    def get_left(self):
        return self.get_left_top()[0]

    def get_top(self):
        return self.get_left_top()[1]

    def __eq__(self, other):
        # assume other is of the same type
        return self.window_handle == other.window_handle