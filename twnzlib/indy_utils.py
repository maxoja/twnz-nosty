import math
from typing import Optional, Any

import numpy as np
import psutil
import pywinctl as pwc
import win32gui
import win32process

from twnzlib.const import GAME_TITLE_PREFIX, PHOENIX_TITLE_INFIX

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

def string_dist(s1, s2):
    # also called levenshtein_distance
    # Create a matrix to store the edit distances
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Initialize the matrix with the base cases
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    # Fill in the matrix using dynamic programming
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)

    return dp[m][n]


def print_map(map_array: np.ndarray, replace_map: dict):
    for row in map_array:
        for cell in row:
            if cell in replace_map:
                cell = replace_map[cell]
            print(str(cell) + ' ', end='')
        print()


def cal_distance(yx1: tuple, yx2: tuple):
    y1, x1 = yx1
    y2, x2 = yx2

    # Calculate the difference in y and x coordinates
    delta_y = y2 - y1
    delta_x = x2 - x1

    # Calculate the Euclidean distance using the Pythagorean theorem
    distance = math.sqrt(delta_y ** 2 + delta_x ** 2)

    return distance