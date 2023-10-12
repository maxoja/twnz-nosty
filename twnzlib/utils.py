import random
from twnzlib import fetch_current_y_x_map_id


def occasional_log(api):
    if random.randint(0, 500) == 50:
        result = fetch_current_y_x_map_id(api)
        print(result)
