import random
from twnz import fetch_current_y_x_map_id


def occasional_log(api, player_name=""):
    if random.randint(0, 500) == 50:
        result = fetch_current_y_x_map_id(api)
        print(player_name, "->", result)
