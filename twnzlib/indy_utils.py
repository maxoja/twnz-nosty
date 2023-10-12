import numpy as np


def print_map(map_array: np.ndarray, replace_map: dict):
    for row in map_array:
        for cell in row:
            if cell in replace_map:
                cell = replace_map[cell]
            print(str(cell) + ' ', end='')
        print()