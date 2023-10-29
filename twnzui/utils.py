import win32gui
import win32con
import win32api
import ctypes
import numpy as np


def mark_window_area(arr, rect, value):
    left, top, right, bottom = rect
    top = max(0, top)
    left = max(0, left)
    bottom = min(arr.shape[0], bottom)
    right = min(arr.shape[1], right)

    if top < bottom and left < right:
        arr[top:bottom, left:right] = value


def get_windows():
    '''Returns windows in z-order (top first)'''
    user32 = ctypes.windll.user32
    lst = []
    top = user32.GetTopWindow(None)
    if not top:
        return lst
    lst.append(top)
    while True:
        next = user32.GetWindow(lst[-1], win32con.GW_HWNDNEXT)
        if not next:
            break
        lst.append(next)
    lst = [ wh for wh in lst if win32gui.IsWindowVisible(wh) and not win32gui.IsIconic(wh) ]
    return lst


def is_window_partially_visible(window_title):
    screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

    screen_array = np.full((screen_height, screen_width), False, dtype=bool)

    target_window_handle = win32gui.FindWindow(None, window_title)

    if not target_window_handle:
        print('window not found')
        return False  # Window not found

    target_rect = win32gui.GetWindowRect(target_window_handle)
    mark_window_area(screen_array, target_rect, True)

    all_win_handles = get_windows()
    for w in all_win_handles:
        if not np.any(screen_array):
            break
        if w != target_window_handle:
            try:
                window_rect = win32gui.GetWindowRect(w)
            except Exception:
                print('invalid window handle found')
                continue
            mark_window_area(screen_array, window_rect, False)
            # print(win32gui.GetWindowText(w))
            # print(window_rect)
            # print(np.any(screen_array))
        else:
            # print(win32gui.GetWindowText(w))
            # print(window_rect)
            # print(np.any(screen_array))
            break

    return np.any(screen_array)


if __name__ == '__main__':
    window_title = "NosTale - (22628)"
    if is_window_partially_visible(window_title):
        print("The window is at least partially visible.")
    else:
        print("The window is not visible or is fully obscured by other windows.")
