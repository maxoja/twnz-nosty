import win32gui
import win32con
import win32api
import numpy as np


def mark_window_area(arr, rect, value=True):
    left, top, right, bottom = rect
    top = max(0, top)
    left = max(0, left)
    bottom = min(arr.shape[0], bottom)
    right = min(arr.shape[1], right)

    if top < bottom and left < right:
        arr[top:bottom, left:right] = value


def is_window_partially_visible(window_title):
    screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

    screen_array = np.full((screen_height, screen_width), False, dtype=bool)

    target_window_handle = win32gui.FindWindow(None, window_title)

    if not target_window_handle:
        return False  # Window not found

    target_rect = win32gui.GetWindowRect(target_window_handle)
    mark_window_area(screen_array, target_rect)

    all_win_handles = []

    def enum_windows_callback(window_handle, _):
        all_win_handles.append(window_handle)

    win32gui.EnumWindows(enum_windows_callback, None)

    for w in all_win_handles:
        if w != target_window_handle:
            window_rect = win32gui.GetWindowRect(w)
            mark_window_area(screen_array, window_rect, False)
        else:
            break

    return np.any(screen_array)


if __name__ == '__main__':
    window_title = "NosTale"
    if is_window_partially_visible(window_title):
        print("The window is at least partially visible.")
    else:
        print("The window is not visible or is fully obscured by other windows.")
