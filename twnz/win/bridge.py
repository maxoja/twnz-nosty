import time

import pyautogui
import win32api
import win32con
import win32gui
from pywinctl._pywinctl_win import Win32Window

from twnz.win.basic import get_foreground_win, get_window_of_handle


def show_win_with_small_delay_if_not_already_handle(handle: int):
    return show_win_with_small_delay_if_not_already(get_window_of_handle(handle))


def show_win_with_small_delay_if_not_already(window:Win32Window):
    # this function was optimised from 0.11 to 0.0005
    # this method doesn't handle None
    if window is None:
        return
    current_fground_win = get_foreground_win()
    if current_fground_win is not None and window.getHandle() == current_fground_win.getHandle():
        return
    rect = win32gui.GetWindowRect(window.getHandle())
    maximized = window.isMaximized
    win32gui.ShowWindow(window.getHandle(), win32con.SW_RESTORE)
    win32api.keybd_event(0x12, 0, 0, 0)
    win32api.keybd_event(0x12, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32gui.SetForegroundWindow(window.getHandle())
    if maximized:
        window.maximize()
    else:
        window.moveTo(newLeft=rect[0], newTop=rect[1])
        window.resizeTo(newWidth=rect[2]-rect[0], newHeight=rect[3]-rect[1])
    # while not win32gui.IsWindowVisible(window.getHandle()):
    #     pass
    # time.sleep(0.0)
