from mud.entities.room import Room
from mud.event import Event
from mud.game_entity import GameEntity


class RoomEntity(GameEntity):
    @classmethod
    def query_by_room_uid(cls, uid, game=None):
        if not game:
            game = cls.get_game()

        results = [
            cls(game, actor)
            for actor in cls.query()
            if actor.get("room_uid", None) == uid
        ]

        return results

    def format_room_flags_to(self, other):
        return ""

    def get_room(self):
        return Room.find_by_uid(self.room_uid)

    def format_room_name_to(self, other):
        return self.room_name

    def event_to_room(self, name, data=None, room=None):
        # TODO broadcast to engine
        print("TODO: Implement event broadcast for {} with data {}".format(
            name,
            repr(data)
        ))
        event = Event(name, data)
        return event

    def set_room(self, room):
        self.room_id = room.id
        self.room_uid = room.uid

