from enum import Enum, auto
from typing import Optional, Tuple

import pyautogui
import win32gui
from pywinctl._pywinctl_win import Win32Window

from twnzui.windows import capture_and_crop_window, HAYSTACK_PATH
from twnzui.indy_utils import show_win_with_small_delay


class Locator(Enum):
    MAP_BUTTON = auto()
    MP_LABEL = auto()
    NOSTALE_TITLE = auto()
    AVATAR_BALL = auto()

    def get_img_path(self):
        if self == Locator.AVATAR_BALL:
            return 'src\\locator\\avatar_ball.png'
        if self == Locator.MAP_BUTTON:
            return 'src\\locator\\map_button.png'
        if self == Locator.MP_LABEL:
            return 'src\\locator\\mp_label.png'
        if self == Locator.NOSTALE_TITLE:
            return 'src\\locator\\nostale_title.png'
        else:
            raise Exception('undefined img path for enum ' + str(self.name))

    def find_local_rect_on_window(self, win: Win32Window) -> Optional[Tuple[int, int, int, int]]:
        show_win_with_small_delay(win)
        l, t, r, b = win32gui.GetWindowRect(win.getHandle())
        cropped = capture_and_crop_window(win, 0, 0, r-l, b-t)
        if cropped == None:
            return None
        cropped.save(HAYSTACK_PATH)

        try:
            result = pyautogui.locate(self.get_img_path(), HAYSTACK_PATH, grayscale=True)
            if result is not None:
                print('located', self, 'at', result, 'for', win.title)
            return result
        except pyautogui.ImageNotFoundException:
            return None

    def find_global_rect_on_window(self, win:Win32Window) -> Optional[Tuple[int, int, int ,int]]:
        rect = self.find_local_rect_on_window(win)
        if rect is None:
            return None
        ll, lt, lw, lh = rect
        gl, gt, gw, gh = win32gui.GetWindowRect(win.getHandle())
        rect = (ll+gl, lt+gt, lw+gw, lh+gh)
        return rect
