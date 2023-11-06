from typing import List, Optional, Tuple, Any

import requests
import json

import pyautogui
from pywinctl._pywinctl_win import Win32Window

from twnzlib.const import GAME_TITLE_POSTFIX, GAME_TITLE_PREFIX
from twnzui.indy_utils import show_win_with_small_delay, get_monitor_from_window, get_screen_dimensions_for_monitor

TEMP_PNG = "eieitemp.png"

NAME = "name"
LEVEL = "level"

HAYSTACK_PATH = 'haystacktemp.png'


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


def get_game_windows_with_name_level_port(game_wins: List[Win32Window]) -> List[Tuple[Win32Window, str, str, int]]:
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
        player_lvl_str = temp_img_to_text(LEVEL, i)
        result.append((w, player_name, player_lvl_str, int(port_title)))
    for t in result:
        print(t)
    return result


def crop_player_level_img(window, i:int):
    fname = f'{LEVEL}-{i}-{TEMP_PNG}'
    capture_and_crop_window(window, lleft=80, ltop=30, lwidth=30, lheight=20).save(fname)

def crop_player_name_img(window, i:int):
    fname = f'{NAME}-{i}-{TEMP_PNG}'
    capture_and_crop_window(window, lleft=110, ltop=30, lwidth=137, lheight=20).save(fname)

