from collections import deque


def find_walk_path(map_array, starting_point, end_point):
    # Define possible movement directions (up, down, left, right).
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    # Get the dimensions of the map array.
    rows, cols = len(map_array), len(map_array[0])

    # Create a visited array to keep track of visited cells.
    visited = [[False] * cols for _ in range(rows)]

    # Create a queue for the BFS algorithm and initialize it with the starting point.
    queue = deque()
    queue.append(starting_point)

    # Create a dictionary to store the parent of each cell.
    parent = {}

    # Perform BFS to find the path from starting_point to end_point.
    while queue:
        y, x = queue.popleft()

        # Check if we've reached the destination.
        if (y, x) == end_point:
            break

        for dy, dx in directions:
            new_y, new_x = y + dy, x + dx

            # Check if the new position is within the map boundaries and is walkable.
            if 0 <= new_y < rows and 0 <= new_x < cols and map_array[new_y][new_x] == 1 and not visited[new_y][new_x]:
                visited[new_y][new_x] = True
                queue.append((new_y, new_x))
                parent[(new_y, new_x)] = (y, x)

    # Reconstruct the path from the destination to the starting point.
    path = []
    current_point = end_point
    while current_point != starting_point:
        path.append(current_point)
        current_point = parent[current_point]
    path.append(starting_point)

    # Reverse the path to start from the starting point.
    path.reverse()

    return path


def simplify_path(walking_path):
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
            if abs(delta_x) + abs(delta_y) <= 3:
                continue

        # Otherwise, add the current point to the simplified path
        simplified_path.append(point)
        prev_point = point

    return simplified_path


# Example usage:
if __name__ == "__main__":
    # Test for path simplifier
    walking_path = [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (1, 2), (1, 3), (0, 3)]
    simplified = simplify_path(walking_path)
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

    path = find_walk_path(map_array, starting_point, end_point)
    print('path of map')
    print('\n'.join(str(row) for row in map_array))
    print(path)
