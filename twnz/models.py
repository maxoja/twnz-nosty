class MapEntity:
    def __init__(self, map_entity: dict):
        self.items = [ItemEntity(item) for item in map_entity.get('items', [])]
        self.monsters = [MonsterEntity(monster) for monster in map_entity.get('monsters', [])]
        self.npcs = [NpcEntity(npc) for npc in map_entity.get('npcs', [])]
        self.players = [PlayerEntity(player) for player in map_entity.get('players', [])]
        self.type = map_entity.get('type', 0)

    def find_item_with_id(self, id):
        for i in self.items:
            if i.id == id:
                return i
        return None

    def __str__(self):
        item_str = "\n".join([str(item) for item in self.items])
        monster_str = "\n".join([str(monster) for monster in self.monsters])
        npc_str = "\n".join([str(npc) for npc in self.npcs])
        player_str = "\n".join([str(player) for player in self.players])

        return f"Type: {self.type}\nItems:\n{item_str}\n\nMonsters:\n{monster_str}\n\nNPCs:\n{npc_str}\n\nPlayers:\n{player_str}"

class ItemEntity:
    def __init__(self, item_data):
        self.id = item_data['id']
        self.name = item_data['name']
        self.owner_id = item_data['owner_id']
        self.quantity = item_data['quantity']
        self.vnum = item_data['vnum']
        self.x = item_data['x']
        self.y = item_data['y']

    def __str__(self):
        return f"Item Entity: ID: {self.id}, Name: {self.name}, Owner ID: {self.owner_id}, Quantity: {self.quantity}, Vnum: {self.vnum}, X: {self.x}, Y: {self.y}"

class MonsterEntity:
    def __init__(self, monster_data):
        self.hp_percent = monster_data['hp_percent']
        self.id = monster_data['id']
        self.mp_percent = monster_data['mp_percent']
        self.name = monster_data['name']
        self.vnum = monster_data['vnum']
        self.x = monster_data['x']
        self.y = monster_data['y']

    def __str__(self):
        return f"Monster : HP Percent: {self.hp_percent}, ID: {self.id}, MP Percent: {self.mp_percent}, Name: {self.name}, Vnum: {self.vnum}, X: {self.x}, Y: {self.y}"

class NpcEntity:
    def __init__(self, npc_data):
        self.hp_percent = npc_data['hp_percent']
        self.id = npc_data['id']
        self.mp_percent = npc_data['mp_percent']
        self.name = npc_data['name']
        self.vnum = npc_data['vnum']
        self.x = npc_data['x']
        self.y = npc_data['y']

    def __str__(self):
        return f"NPC Entity: HP Percent: {self.hp_percent}, ID: {self.id}, MP Percent: {self.mp_percent}, Name: {self.name}, Vnum: {self.vnum}, X: {self.x}, Y: {self.y}"

class PlayerEntity:
    def __init__(self, player_data):
        self.champion_level = player_data['champion_level']
        self.family = player_data['family']
        self.hp_percent = player_data['hp_percent']
        self.id = player_data['id']
        self.level = player_data['level']
        self.mp_percent = player_data['mp_percent']
        self.name = player_data['name']
        self.x = player_data['x']
        self.y = player_data['y']

    def __str__(self):
        return f"Player Entity: Champion Level: {self.champion_level}, Family: {self.family}, HP Percent: {self.hp_percent}, ID: {self.id}, Level: {self.level}, MP Percent: {self.mp_percent}, Name: {self.name}, X: {self.x}, Y: {self.y}"


class PlayerInfo:
    def __init__(self, champion_level, hp_percent, id, is_resting, level, map_id, mp_percent, name, x, y):
        self.champion_level = champion_level
        self.hp_percent = hp_percent
        self.id = id
        self.is_resting = is_resting
        self.level = level
        self.map_id = map_id
        self.mp_percent = mp_percent
        self.name = name
        self.x = x
        self.y = y

    @classmethod
    def from_dict(cls, data):
        return cls(
            data['champion_level'],
            data['hp_percent'],
            data['id'],
            data['is_resting'],
            data['level'],
            data['map_id'],
            data['mp_percent'],
            data['name'],
            data['x'],
            data['y']
        )

    def to_dict(self):
        return {
            'champion_level': self.champion_level,
            'hp_percent': self.hp_percent,
            'id': self.id,
            'is_resting': self.is_resting,
            'level': self.level,
            'map_id': self.map_id,
            'mp_percent': self.mp_percent,
            'name': self.name,
            'x': self.x,
            'y': self.y
        }

    def __str__(self):
        return f"PlayerInfo(champion_level={self.champion_level}, hp_percent={self.hp_percent}, id={self.id}, " \
               f"is_resting={self.is_resting}, level={self.level}, map_id={self.map_id}, mp_percent={self.mp_percent}, " \
               f"name='{self.name}', x={self.x}, y={self.y})"


if __name__ == '__main__':
    json_data = {
        'items': [{'id': 2527585, 'name': 'Gold', 'owner_id': 62426, 'quantity': 125, 'vnum': 1046, 'x': 14, 'y': 199}],
        'monsters': [
            {'hp_percent': 100, 'id': 2857, 'mp_percent': 100, 'name': 'Baby Fox', 'vnum': 0, 'x': 5, 'y': 152}],
        'npcs': [
            {'hp_percent': 0, 'id': -97, 'mp_percent': 0, 'name': 'Time-Space Portal', 'vnum': 930, 'x': 159, 'y': 43}],
        'players': [{'champion_level': 0, 'family': '-', 'hp_percent': 43, 'id': 62426, 'level': 19, 'mp_percent': 78,
                     'name': 'BotPlayer', 'x': 14, 'y': 199}],
        'type': 19
    }

    map_entity = MapEntity(json_data)
    print(map_entity)