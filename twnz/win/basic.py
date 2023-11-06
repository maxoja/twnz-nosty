from typing import Optional, Any

import psutil
import pywinctl as pwc
import win32gui
import win32process

from twnz.const import PHOENIX_TITLE_INFIX, GAME_TITLE_PREFIX


def get_window_of_handle(handle: int):
    for w in pwc.getAllWindows():
        if w.getHandle() == handle:
            return w
    return None


def get_game_pid_from_bot_port(bot_port: int):
    for conn in psutil.net_connections(kind='tcp'):
        if conn.laddr.port == bot_port:
            return conn.pid


def get_win_of_pid(looking_pid: int) -> Optional[Any]:
    all_win = pwc.getAllWindows()
    for w in all_win:
        threadid, pid = win32process.GetWindowThreadProcessId(w.getHandle())
        title = win32gui.GetWindowText(w.getHandle())
        if pid == looking_pid and "Nostale" not in title and (title.strip() == "" or "NosTale" in title):
            print('looking for pid', looking_pid, 'against', pid, ' --> ',title)
            # intentionally use NosTale instead of Nostale
            return w
    return None


def get_all_handles():
    all_wins = pwc.getAllWindows()
    handles = [w.getHandle() for w in all_wins]
    return handles


def get_phoenix_windows():
    return [ w for w in pwc.getAllWindows() if PHOENIX_TITLE_INFIX in w.title ]


def get_game_windows(handle_blacklist=None):
    if handle_blacklist is None:
        handle_blacklist = []
    return [ w for w in pwc.getAllWindows() if GAME_TITLE_PREFIX in w.title and w.getHandle() not in handle_blacklist]


def process_active(pid: int or str) -> bool:
    try:
        process = psutil.Process(pid)
    except psutil.Error as error:  # includes NoSuchProcess error
        return False
    if psutil.pid_exists(pid) and process.status() == psutil.STATUS_RUNNING:
        return True
