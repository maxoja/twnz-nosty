from phoenixapi import phoenix
import json
from time import sleep
from twnzlib import config


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
