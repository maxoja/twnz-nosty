import time

from twnz import fetch, cal_distance
from twnz.models import MapEntity, PlayerEntity


def find_closest_monster_autoload(api, vnum_whitelist=None, vnum_blacklist=None):
    if vnum_blacklist is None:
        vnum_blacklist = []
    if vnum_whitelist is None:
        vnum_whitelist = []
    map_entity: MapEntity = fetch.fetch_map_entities(api)
    player_info: PlayerEntity = fetch.fetch_player_info(api)
    print(map_entity)
    return find_closest_monster(map_entity, player_info, vnum_whitelist, vnum_blacklist)


def find_closest_monster(map_entity: MapEntity, player_info: PlayerEntity, vnum_whitelist=None, vnum_blacklist=None):
    if vnum_blacklist is None:
        vnum_blacklist = []
    if vnum_whitelist is None:
        vnum_whitelist = []

    
    player_info_y = player_info['y']
    player_info_x = player_info['x']
    monsters = map_entity.monsters[::]
    if len(monsters) == 0:
        return None

    if len(vnum_whitelist) > 0 and len(vnum_blacklist) > 0:
        raise Exception("it is unexpected to have both whitelist and blacklist as non-empty")

    if len(vnum_whitelist) == 0 and len(vnum_blacklist) == 0:
        # every monster
        pass
    elif len(vnum_whitelist) > 0:
        monsters = [ m for m in monsters if m.vnum in vnum_whitelist ]
    elif len(vnum_blacklist) > 0:
        monsters = [m for m in monsters if m.vnum not in vnum_blacklist]
    else:
        raise Exception("unexpected case found")

    monsters.sort(key=lambda m: cal_distance((m.y, m.x), (player_info_y, player_info_x)))
    return monsters[0]


def attack_closest_monster_till_it_dies(api, settings_path: str = "D:\\InstantCombat\\basicatk.ini"):
    #settings_path = os.path.join('D:', '\\SteamLibrary', 'steamapps', 'common', 'NosTale', 'default.ini')
    api.load_settings(settings_path)
    target_monster = find_closest_monster_autoload(api)

    while True:
        map_entity = fetch.fetch_map_entities(api)
        found_monster = [m for m in map_entity.monsters if m.id == target_monster.id]
        if len(found_monster) == 0:
            break
        api.attack_monster(monster_id=target_monster.id)
        time.sleep(0.5)
