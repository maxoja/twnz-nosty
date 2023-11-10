import json
from enum import Enum, auto
from typing import Optional, Tuple, Any
from PIL import Image

import mss.tools
import pyautogui
import requests
import win32gui
from pywinctl._pywinctl_win import Win32Window

from twnz.win.const import TEMP_PNG, NAME, LEVEL, HAYSTACK_PATH, BOT_STATUS_TEMP_PNG
from twnz.win.basic import get_monitor_from_window, get_monitor_info
from twnz.win.bridge import show_win_with_small_delay_if_not_already


class Locator(Enum):
    MAP_BUTTON = auto()
    MP_LABEL = auto()
    NOSTALE_TITLE = auto()
    AVATAR_BALL = auto()
    STATE_STOPPED = auto()
    STATE_RUNNING = auto()
    STATE_IDLE = auto()

    def get_img_path(self):
        if self == Locator.AVATAR_BALL:
            return 'src\\locator\\avatar_ball.png'
        if self == Locator.MAP_BUTTON:
            return 'src\\locator\\map_button.png'
        if self == Locator.MP_LABEL:
            return 'src\\locator\\mp_label.png'
        if self == Locator.NOSTALE_TITLE:
            return 'src\\locator\\nostale_title.png'
        if self == Locator.STATE_STOPPED:
            return 'src\\locator\\state_stopped.png'
        if self == Locator.STATE_RUNNING:
            return 'src\\locator\\state_running.png'
        if self == Locator.STATE_IDLE:
            return 'src\\locator\\state_idle.png'
        else:
            raise Exception('undefined img path for enum ' + str(self.name))

    def find_local_rect_on_window(self, win: Win32Window, local_ltwh: Tuple[int, int, int, int] = None) -> Optional[Tuple[int, int, int, int]]:
        show_win_with_small_delay_if_not_already(win)
        if local_ltwh is None:
            l, t, r, b = win32gui.GetWindowRect(win.getHandle())
            l, t, w, h = 0, 0, r-l, b-t
        else:
            l, t, w, h = local_ltwh

        cropped = capture_and_crop_window(win, l, t, w, h, save_now=True, target_path=HAYSTACK_PATH)
        if cropped is None:
            return None

        try:
            result = pyautogui.locate(self.get_img_path(), HAYSTACK_PATH, grayscale=True)
            # if result is not None:
                # print('located', self, 'at', result, 'for', win.title)
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


def ocr_bot_status_img_to_text(url: str="https://tesseract-server.hop.sh/tesseract"):
    fname = BOT_STATUS_TEMP_PNG
    files = {
        'file': (fname, open(fname, 'rb')),
    }
    data = {
        'options': '{"languages":["eng"], "dpi": 119, "pageSegmentationMethod": 7, "ocrEngineMode": 0, "configParams": {"classify_enable_learning": "0", "classify_enable_adaptive_matcher": "0"}}'
    }

    response = requests.post(url, files=files, data=data)
    print(response.text)
    stdout = json.loads(response.text)['data']['stdout'].strip()
    return stdout


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


def capture_and_crop_window(window, lleft, ltop, lwidth, lheight, save_now=False, target_path=TEMP_PNG) -> Optional[Any]:
    try:
        # Get the window's position and size
        win_x, win_y, win_width, win_height = window.left, window.top, window.width, window.height
        monitor_handle = get_monitor_from_window(window.getHandle())
        monitor_info = get_monitor_info(monitor_handle)
        # monitor_id = int(monitor_info['Device'].split('DISPLAY')[-1]) # Intentionally keep it as 1-based not 0-based
        ml, mt, mr, mb = monitor_info['Monitor']

        # Capture the window content and crop it
        gleft = max(ml, win_x + lleft)
        gright = min(win_x + lleft + lwidth, mr)
        gtop = max(ml, win_y + ltop)
        gbottom = min(win_y + ltop + lheight, mb)

        if gright <= gleft or gbottom <= gtop:
            print("Invalid cropping dimensions.")
            return None

        with mss.mss() as sct:
            # mss_monitor = sct.monitors[monitor_id]
            bb = (gleft, gtop, gright, gbottom)
            im = sct.grab(bb)
            print(bb)
            mss.tools.to_png(im.rgb, im.size, output=("mss"+TEMP_PNG))
            screenshot = Image.open("mss"+TEMP_PNG)

        if screenshot is not None and save_now:
            screenshot.save(target_path)
        return screenshot

    except Exception as e:
        print(f"Error capturing window: {str(e)}")
        return None
