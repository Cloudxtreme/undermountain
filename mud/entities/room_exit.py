from mud.game_entity import GameEntity
from mud.entities.room import Room


class RoomExit(GameEntity):
    def get_room(self):
        room = Room.find_by("uid", self.room_uid, game=self.game)
        if room:
            return room

        room = Room.find_by("id", self.room_id, game=self.game)
        if room:
            return room

        return None

    def has_flag(self, flag):
        return False
