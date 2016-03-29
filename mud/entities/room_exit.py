from mud.game_entity import GameEntity
from mud.entities.room import Room


class RoomExit(GameEntity):
    def get_room(self):
        return Room.find_by_uid(self.room_uid)
