import time
import requests
import json

import pywinctl as pwc
import pyautogui
import win32gui
import win32con

TEMP_PNG = "eieitemp.png"



NAME = "name"
LEVEL = "level"


def temp_img_to_text(prefix: str, i: int):
    url = "https://tesseract-server.hop.sh/tesseract"
    psm = 8 if prefix == LEVEL else 3
    fname = f'{prefix}-{i}-{TEMP_PNG}'
    files = {
        'file': (fname, open(fname, 'rb')),
    }
    data = {
        'options': '{"languages":["eng"], "dpi":120, "pageSegmentationMethod": ' + str(psm) + '}'
    }

    response = requests.post(url, files=files, data=data)
    print(response.text)
    return json.loads(response.text)['data']['stdout'].strip()


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
    time.sleep(0.01)


def __get_game_windows():
    return [ w for w in pwc.getAllWindows() if "NosTale - (" in w.title ]


def get_game_windows_with_level_n_name():
    game_wins = __get_game_windows()

    for i, w in enumerate(game_wins):
        __show_win_with_small_delay(w)
        crop_player_level_img_as_text(w, i)
        crop_player_name_img_as_text(w, i)

    result = []
    for i, w in enumerate(game_wins):
        result.append((w, int(temp_img_to_text("name", i)), temp_img_to_text("player", i)))
    for t in result:
        print(t)
    return result


def crop_player_level_img_as_text(window, i:int):
    fname = f'{LEVEL}-{i}-{TEMP_PNG}'
    __capture_and_crop_window(window, left=80, top=30, width=30, height=20).save(fname)

def crop_player_name_img_as_text(window, i:int):
    fname = f'{NAME}-{i}-{TEMP_PNG}'
    __capture_and_crop_window(window, left=110, top=30, width=137, height=20).save(fname)
