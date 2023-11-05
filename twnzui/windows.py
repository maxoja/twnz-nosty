import time
from enum import Enum, auto
from typing import List, Optional, Tuple, Any

import requests
import json

import pyautogui
import win32api
import win32gui
import win32con
from PIL import Image
from pywinctl._pywinctl_win import Win32Window

from twnzlib import get_game_windows
from twnzlib.const import GAME_TITLE_POSTFIX, GAME_TITLE_PREFIX, PHOENIX_TITLE_INFIX

TEMP_PNG = "eieitemp.png"

NAME = "name"
LEVEL = "level"
DELAY = 0.02


def show_win_with_small_delay(window:Win32Window):
    win32gui.ShowWindow(window.getHandle(), win32con.SW_RESTORE)
    pyautogui.press('alt')
    win32gui.SetForegroundWindow(window.getHandle())
    while not win32gui.IsWindowVisible(window.getHandle()):
        pass
    time.sleep(DELAY)


HAYSTACK_PATH = 'haystacktemp.png'


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
        capture_and_crop_window(win, 0, 0, r-l, b-t).save(HAYSTACK_PATH)
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


def temp_img_to_text(prefix: str, i: int, url: str="https://tesseract-server.hop.sh/tesseract"):
    # psm = 8 if prefix == LEVEL else 3
    # dpi = 120 if prefix == LEVEL else 70
    fname = f'{prefix}-{i}-{TEMP_PNG}'
    # print("OCR =", fname, psm)
    files = {
        'file': (fname, open(fname, 'rb')),
    }

    if prefix == LEVEL:
        data = {
            'options': '{"languages":["eng"], "dpi": 120, "pageSegmentationMethod": 8, "ocrEngineMode": 3, "configParams": {"classify_enable_learning": "0", "tessedit_char_whitelist": "012345789+()"}}'
        }
    else:
        data = {
            'options': '{"languages":["eng"], "dpi": 119, "pageSegmentationMethod": 8, "ocrEngineMode": 0, "configParams": {"classify_enable_learning": "0", "classify_enable_adaptive_matcher": "0"}}'
        }

    response = requests.post(url, files=files, data=data)
    print(response.text)
    stdout = json.loads(response.text)['data']['stdout'].strip()
    if prefix == NAME:
        stdout = stdout.split("(")[0]
    return stdout

def get_monitor_from_window(window_handle):
    monitor_handle = win32api.MonitorFromWindow(window_handle, win32con.MONITOR_DEFAULTTONEAREST)
    return monitor_handle

def get_screen_dimensions_for_monitor(monitor_handle):
    try:
        # Get monitor info
        monitor_info = win32api.GetMonitorInfo(monitor_handle)

        # Calculate the screen width and height
        screen_width = monitor_info['Monitor'][2] - monitor_info['Monitor'][0]
        screen_height = monitor_info['Monitor'][3] - monitor_info['Monitor'][1]

        return screen_width, screen_height
    except Exception as e:
        print(f"Error: {e}")
        return None

def capture_and_crop_window(window, lleft, ltop, lwidth, lheight) -> Optional[Any]:
    try:
        # Get the window's position and size
        win_x, win_y, win_width, win_height = window.left, window.top, window.width, window.height
        monitor_handle = get_monitor_from_window(window.getHandle())
        swidth, sheight = get_screen_dimensions_for_monitor(monitor_handle)

        # Capture the window content and crop it
        gleft = max(0, win_x + lleft)
        gright = min(win_x + lleft + lwidth, swidth)
        gtop = max(0, win_y + ltop)
        gbottom = min(win_y + ltop + lheight, sheight)

        if gright <= gleft or gbottom <= gtop:
            print("Invalid cropping dimensions.")
            return None

        screenshot = pyautogui.screenshot(
            region=(gleft, gtop, gright - gleft, gbottom - gtop))

        return screenshot

    except Exception as e:
        print(f"Error capturing window: {str(e)}")
        return None


def get_game_windows_with_name_level_port(game_wins: List[Win32Window]) -> List[Tuple[Win32Window, str, int, int]]:
    for i, w in enumerate(game_wins):
        show_win_with_small_delay(w)
        crop_player_level_img(w, i)
        crop_player_name_img(w, i)

    result = []
    for i, w in enumerate(game_wins):
        port_title = w.title
        port_title = port_title.replace(GAME_TITLE_PREFIX, "")
        port_title = port_title.replace(GAME_TITLE_POSTFIX, "")
        player_name = temp_img_to_text(NAME, i)
        player_lvl = int(temp_img_to_text(LEVEL, i))
        result.append((w, player_name, player_lvl, int(port_title)))
    for t in result:
        print(t)
    return result


def crop_player_level_img(window, i:int):
    fname = f'{LEVEL}-{i}-{TEMP_PNG}'
    capture_and_crop_window(window, lleft=80, ltop=30, lwidth=30, lheight=20).save(fname)

def crop_player_name_img(window, i:int):
    fname = f'{NAME}-{i}-{TEMP_PNG}'
    capture_and_crop_window(window, lleft=110, ltop=30, lwidth=137, lheight=20).save(fname)

