from collections import deque

import numpy as np

from twnz import print_map


def find_walk_path_pruned(map_array: np.ndarray, start_yx: tuple, dest_yx: tuple):
    path_points = __find_walk_path(map_array, start_yx, dest_yx)
    return __simplify_path(path_points)


def __debug_path_finding(map_array: np.ndarray, start_yx: tuple, dest_yx: tuple, walk_path: list):
    logging_map = np.copy(map_array)
    start_y, start_x = start_yx
    dest_y, dest_x = dest_yx
    for y,x in walk_path:
        logging_map[y][x] = 4
    logging_map[start_y][start_x] = 2
    logging_map[dest_y][dest_x] = 3
    print_map(logging_map, {2: 'S', 3: 'D', 1: ' ', 4: '+'})
    print('start', start_yx, 'dest', dest_yx)


def __find_walk_path(map_array: np.ndarray, start_yx: tuple, dest_yx: tuple) -> [tuple]:
    __debug_path_finding(map_array, start_yx, dest_yx, [])

    # Define possible movement directions (up, down, left, right).
    dir_yx_deltas = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    # Get the dimensions of the map array.
    rows, cols = len(map_array), len(map_array[0])

    # Create a visited array to keep track of visited cells.
    visited = [[False] * cols for _ in range(rows)]

    # Create a queue for the BFS algorithm and initialize it with the starting point.
    queue = deque()
    queue.append(start_yx)

    # Create a dictionary to store the parent of each cell.
    parent = {}

    # Perform BFS to find the path from starting_point to end_point.
    while queue:
        y, x = queue.popleft()

        # Check if we've reached the destination.
        if (y, x) == dest_yx:
            break
        if visited[y][x]:
            continue

        visited[y][x] = True

        for dy, dx in dir_yx_deltas:
            new_y, new_x = y + dy, x + dx

            if not new_y in range(rows) or not new_x in range(cols):
                continue
            if map_array[new_y][new_x] == 0:
                continue
            if visited[new_y][new_x]:
                continue

            queue.append((new_y, new_x))
            parent[(new_y, new_x)] = (y, x)

    # Reconstruct the path from the destination to the starting point.
    path = []
    current_point = dest_yx
    while current_point != start_yx:
        path.append(current_point)
        current_point = parent[current_point]
    path.append(start_yx)
    path = path[::-1] # this returns None

    __debug_path_finding(map_array, start_yx, dest_yx, path)
    return path


def __simplify_path(walking_path: [tuple]):
    if len(walking_path) < 2:
        return walking_path

    simplified_path = [walking_path[0]]
    prev_point = walking_path[0]

    for point in walking_path[1:]:
        # Calculate the direction from the previous point to the current point
        delta_y = point[0] - prev_point[0]
        delta_x = point[1] - prev_point[1]

        # If the direction is 0, 90, 180, or 270 degrees, skip the current point
        if delta_x == 0 or delta_y == 0 or abs(delta_x) == abs(delta_y):
            if abs(delta_x) + abs(delta_y) <= 5:
                continue

        # Otherwise, add the current point to the simplified path
        simplified_path.append(point)
        prev_point = point

    return simplified_path


# Example usage:
if __name__ == "__main__":
    # Test for path simplifier
    walking_path = [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (1, 2), (1, 3), (0, 3)]
    simplified = __simplify_path(walking_path)
    print("before/after simplify")
    print(walking_path)
    print(simplified)
    print()

    # Test for path points calculation
    map_array = [
        [1, 1, 1, 0, 1],
        [0, 0, 1, 1, 1],
        [1, 0, 1, 0, 0],
        [1, 1, 1, 0, 1],
        [1, 1, 1, 0, 1],
        [1, 0, 1, 1, 1]
    ]

    starting_point = (0, 0)
    end_point = (3, 4)

    path = __find_walk_path(map_array, starting_point, end_point)
    print('path of map')
    print('\n'.join(str(row) for row in map_array))
    print(path)
