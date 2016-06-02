from mud.entities.room import Room
from mud.event import Event
from mud.game_entity import GameEntity


class RoomEntity(GameEntity):
    INDEXES = ['id', 'room_uid', 'room_id']

    @classmethod
    def query_by_room_uid(cls, uid, game):
        return cls.query_by("room_uid", uid, game=game)

    def format_room_flags_to(self, other):
        return ""

    def get_room(self):
        room = Room.get_by_uid(self.room_uid, game=self.game)
        if room is not None:
            return room

        # TODO Make this figure out if this entity can be present in one
        # of these rooms, otherwise.. return None
        rooms = list(Room.query_by_id(self.room_id, game=self.game))
        if rooms:
            room = rooms[0]
            self.set_room(room)
            return self.get_room()

        # FIXME Make this a fallback configuration setting somewhere
        tol = Room.find_by("id", "3001", game=self.game)
        print("tol")
        if tol:
            self.set_room(tol)
            return self.get_room()

        return None

    def format_room_name_to(self, other):
        return self.room_name

    def event_to_room(self, name, data=None, room=None, blockable=False):
        if data is None:
            data = {}

        data["source"] = self

        event = Event(name, data, blockable=blockable)

        if room is None:
            room = self.get_room()

        room.handle_event(event)

        return event

    def set_room(self, room):
        self.room_id = room.id
        self.room_uid = room.uid

    def say(self, message, ooc=False, trigger=True):
        if trigger:
            event_data = {
                "channel": "say",
                "message": message,
            }

            event = self.event_to_room("saying", event_data, blockable=True)

            if event.is_blocked():
                return

        ooc_string = "[OOC] " if ooc else ""

        self.echo("{{MYou say {}{{x'{{m{}{{x'".format(
            ooc_string,
            message,
            trigger=trigger
        ))
        self.act_around("{{M[actor.name] says {}{{x'{{m{}{{x'".format(
            ooc_string,
            message,
            trigger=trigger
        ))

        if trigger:
            self.event_to_room("said", event_data)

    def format_act_template(self, template, actor, other):
        message = template

        # FIXME make more efficient
        name_to_other = actor.format_name_to(other)
        replaces = {
            "actor.name": name_to_other,
            "object.name": name_to_other,
        }

        for field, value in replaces.items():
            if field in message:
                message = message.replace("[" + field + "]", value)

        return message

    def act_to(self, other, template, trigger=True):
        message = self.format_act_template(template, actor=self, other=other)

        if trigger:
            event_data = {
                "message": message,
            }

            event = self.event_to_room("acting", event_data)

            if event.is_blocked():
                return

        other.echo(message)
        # TODO look for triggers to fire

        if trigger:
            event = self.event_to_room("acted", event_data)

    def act_around(self, template, trigger=True, exclude=None):
        room = self.get_room()

        for other in room.get_actors(exclude=self):
            if exclude is not None and (other == exclude or other in exclude):
                continue
            self.act_to(other, template, trigger=trigger)

    def name_like(self, name):
        return self.name.lower().startswith(name.lower())

    def query_room_entities(self, types=None, visible=True, keyword=None):
        """
        Query the things in the room, using the types provided.
        Types is a list of GameEntity classes.
        """
        # FIXME use setting
        if keyword == "self":
            yield self

        else:
            if type(types) is not list:
                return None

            room = self.get_room()
            room_uid = room.uid

            for type_class in types:
                for result in type_class.query_by("room_uid", room_uid, game=self.game):
                    if visible and not self.can_see(result):
                        continue

                    if keyword is not None and not result.name_like(keyword):
                        continue

                    yield result

    def find_room_entity(self, *args, **kwargs):
        """
        Find "something" in the Room, that meets the criteria requested.
        See query_room_entities for help on parameters.
        Types is used to define the order
        """
        for entity in self.query_room_entities(*args, **kwargs):
            return entity
