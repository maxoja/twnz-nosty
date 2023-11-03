import time
import requests
import json

import pyautogui
import win32gui
import win32con

from twnzlib import get_game_windows
from twnzlib.const import GAME_TITLE_POSTFIX, GAME_TITLE_PREFIX, PHOENIX_TITLE_INFIX

TEMP_PNG = "eieitemp.png"


NAME = "name"
LEVEL = "level"
DELAY = 0.02


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


def __capture_and_crop_window(window, left, top, width, height):
    try:
        # Get the window's position and size
        x, y, win_width, win_height = window.left, window.top, window.width, window.height

        # Calculate the cropping coordinates
        crop_left = max(left, 0)
        crop_top = max(top, 0)
        crop_right = min(left + width, win_width)
        crop_bottom = min(top + height, win_height)

        if crop_right <= crop_left or crop_bottom <= crop_top:
            print("Invalid cropping dimensions.")
            return None

        # Capture the window content and crop it
        screenshot = pyautogui.screenshot(
            region=(x + crop_left, y + crop_top, crop_right - crop_left, crop_bottom - crop_top))


        return screenshot

    except Exception as e:
        print(f"Error capturing window: {str(e)}")
        return None


def __show_win_with_small_delay(window):
    win32gui.ShowWindow(window.getHandle(), win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(window.getHandle())
    while not win32gui.IsWindowVisible(window.getHandle()):
        pass
    time.sleep(DELAY)


def get_game_windows_with_name_level_port():
    game_wins = get_game_windows()

    for i, w in enumerate(game_wins):
        __show_win_with_small_delay(w)
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
    __capture_and_crop_window(window, left=80, top=30, width=30, height=20).save(fname)

def crop_player_name_img(window, i:int):
    fname = f'{NAME}-{i}-{TEMP_PNG}'
    __capture_and_crop_window(window, left=110, top=30, width=137, height=20).save(fname)
