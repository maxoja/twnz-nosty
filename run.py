from phoenixapi import phoenix
from time import sleep
import json
from twnz import *



if __name__ == "__main__":
    # Put the port from the bot title, it should look something like
    # [Lv 99.(+80) CharacterName] - Phoenix Bot:123123
    port = 4772
    # host = "82.27.140.49"
    api = phoenix.Api(port)
    points = []

    # Logs all the packets that are sent/received from the client
    while api.working():
        if not api.empty():
            msg = api.get_message()
            json_msg = json.loads(msg)

            if json_msg["type"] == phoenix.Type.packet_send.value:
                print("[SEND]: " + json_msg["packet"])
            elif json_msg["type"] == phoenix.Type.packet_recv.value:

                packet = json_msg['packet']
                head = packet.split()[0]

                if head == 'hidn':
                    print("[RECV]: " + json_msg["packet"])
                    _, deg, x, y = eval("(" + ",".join(packet.split()[1:])+")")
                    points.append((x, y, deg))
                    print("*** hidn received, saving a marker", points[-1])
                    if len(points) > 2:
                        points = points[1:]
                    if len(points) >= 2:
                        print("*** intersection from last 2 cracks", str(find_intersection(points[0], points[1])))
                else:
                    pass
        else:
            sleep(0.01) 

    api.close()