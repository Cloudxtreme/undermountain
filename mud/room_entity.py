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
        room = Room.get_by_uid(self.room_uid)
        if room is not None:
            return room

        # TODO Make this figure out if this entity can be present in one
        # of these rooms, otherwise.. return None
        rooms = Room.query_by_id(self.room_id)
        if rooms:
            room = rooms[0]
            self.room_uid = room.uid
            return room

        return None

    def format_room_name_to(self, other):
        return self.room_name

    def event_to_room(self, name, data=None, blockable=False, room=None):
        import gevent

        if data is None:
            data = {}

        data["source"] = self

        event = Event(name, data, blockable=blockable)

        if room is None:
            room = self.get_room()

        room.handle_event(event)
        # gevent.spawn(room.handle_event, event)

        return event

    def set_room(self, room):
        self.room_id = room.id
        self.room_uid = room.uid
