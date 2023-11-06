import win32gui
import win32con
import win32api
import ctypes
import numpy as np

from twnzui.indy_utils import get_all_monitor_handles


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

def is_window_partially_visible(target_window_handle: int):
    monitor_handles = get_all_monitor_handles()
    for m in monitor_handles:
        if is_window_partially_visible_on_monitor(target_window_handle, m):
            return True
    return False

def is_window_partially_visible_on_monitor(target_window_handle: int, monitor_handle: int):

    monitor_info = win32api.GetMonitorInfo(monitor_handle)
    monitor_rect_ltrb = monitor_info['Monitor']
    screen_width = monitor_rect_ltrb[2] - monitor_rect_ltrb[0]
    screen_height = monitor_rect_ltrb[3] - monitor_rect_ltrb[1]
    screen_array = np.full((screen_height, screen_width), False, dtype=bool)

    if not target_window_handle:
        print('window not found')
        return False  # Window not found

    target_rect_ltrb = win32gui.GetWindowRect(target_window_handle)
    target_rect_ltrb = (
        target_rect_ltrb[0] - monitor_rect_ltrb[0],
        target_rect_ltrb[1] - monitor_rect_ltrb[1],
        target_rect_ltrb[2] - monitor_rect_ltrb[0],
        target_rect_ltrb[3] - monitor_rect_ltrb[1]
    )
    mark_window_area(screen_array, target_rect_ltrb, True)

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
