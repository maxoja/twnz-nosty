import time

import pyautogui
import win32api
import win32con
import win32gui
from pywinctl._pywinctl_win import Win32Window


DELAY = 0.02


def show_win_with_small_delay(window:Win32Window):
    win32gui.ShowWindow(window.getHandle(), win32con.SW_RESTORE)
    pyautogui.press('alt')
    win32gui.SetForegroundWindow(window.getHandle())
    while not win32gui.IsWindowVisible(window.getHandle()):
        pass
    time.sleep(DELAY)


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
