import time

import pyautogui
import win32api
import win32con
import win32gui
from pywinctl._pywinctl_win import Win32Window

from twnz.win.basic import get_foreground_win


def show_win_with_small_delay_if_not_already(window:Win32Window):
    # this function was optimised from 0.11 to 0.0005
    current_fground_win = get_foreground_win()
    if current_fground_win is not None and window.getHandle() == current_fground_win.getHandle():
        return
    win32gui.ShowWindow(window.getHandle(), win32con.SW_RESTORE)
    win32api.keybd_event(0x12, 0, 0, 0)
    win32api.keybd_event(0x12, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32gui.SetForegroundWindow(window.getHandle())
    # while not win32gui.IsWindowVisible(window.getHandle()):
    #     pass
    # time.sleep(0.0)
