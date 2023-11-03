import numpy as np
import pywinctl as pwc

from twnzlib.const import GAME_TITLE_PREFIX, PHOENIX_TITLE_INFIX


def get_phoenix_windows():
    return [ w for w in pwc.getAllWindows() if PHOENIX_TITLE_INFIX in w.title ]

def get_game_windows():
    return [ w for w in pwc.getAllWindows() if GAME_TITLE_PREFIX in w.title ]

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