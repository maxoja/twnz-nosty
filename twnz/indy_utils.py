import math

import numpy as np

import psutil


def kill_process_tree(pid):
    print('killing', pid)
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)  # Get all child processes recursively.
        for child in children:
            child.terminate()  # Terminate child processes.
        parent.terminate()  # Terminate the parent process.
        parent.wait()  # Wait for the parent process to finish.
    except psutil.NoSuchProcess:
        print(f"Process with PID {pid} not found.")
    except psutil.AccessDenied:
        print(f"Access denied. You may need administrative privileges to terminate the process.")


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


