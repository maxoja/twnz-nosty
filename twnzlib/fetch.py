from typing import Union

from phoenixapi import phoenix
import json
from time import sleep
from twnzlib import config
from twnzlib.models import MapEntity


def fetch_current_y_x_map_id(api: phoenix.Api):
    api.query_player_information()
    # at this point assume that api.working()
    while api.working():
        if not api.empty():
            msg = api.get_message()
            json_msg = json.loads(msg)

            if not json_msg["type"] == phoenix.Type.query_player_info.value:
                continue

            packet = json_msg['player_info']
            # this below actually returns y,x despite how it looks
            return packet['y'], packet['x'], packet['map_id']
        else:
            sleep(config.API_INTERVAL)


def fetch_player_info(api: phoenix.Api):
    api.query_player_information()
    # at this point assume that api.working()
    while api.working():
        if not api.empty():
            msg = api.get_message()
            json_msg = json.loads(msg)

            if not json_msg["type"] == phoenix.Type.query_player_info.value:
                continue

            packet = json_msg['player_info']
            return packet
        else:
            sleep(config.API_INTERVAL)


def fetch_map_entities(api: phoenix.Api) -> MapEntity:
    api.query_map_entities()
    # at this point assume that api.working()
    while api.working():
        if not api.empty():
            msg = api.get_message()
            json_msg = json.loads(msg)

            if not json_msg["type"] == phoenix.Type.query_map_entities.value:
                continue

            return MapEntity(json_msg)
        else:
            sleep(config.API_INTERVAL)


def print_nicely(o: Union[dict, list], depth=0):
    TAB = " "
    MAX_TOP_LAYER = 2
    high_level = depth < MAX_TOP_LAYER
    if high_level and type(o) is dict:
        for k,v in o.items():
            print(TAB*depth + str(k))
            print_nicely(v, depth+1)
            print()
    elif high_level and type(o) is list:
        for v in o:
            print_nicely(v, depth + 1)
    else:
        # non collection object
        print(TAB*depth + str(o))