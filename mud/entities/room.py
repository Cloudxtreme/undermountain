from mud.game_entity import GameEntity


class Room(GameEntity):
    """
    ROOM
    A container that Actors, Objects, and general "things" can be in.
    """
    UNIQUE_INDEXES = ["uid"]
    INDEXES = ["id"]
    COLLECTION_NAME = 'rooms'

    def query_entities(self, exclude=None):
        for actor in self.get_actors():
            yield actor

        for obj in self.query_objects():
            yield obj

    def query_objects(self):
        from mud.entities.object import Object

        for obj in Object.query_by_room_uid(self.uid, game=self.game):
            yield obj

    def get_actors(self, exclude=None):
        """
        Get all the Actors in this Room.
        """
        from mud.entities.actor import Actor
        from mud.entities.character import Character

        # FIXME use some kind of reusable filtering function
        for actor in Actor.query_by_room_uid(self.uid, game=self.game):
            if actor == exclude:
                continue

            yield actor

        for actor in Character.query_by_room_uid(self.uid, game=self.game):
            if actor == exclude:
                continue

            yield actor

    def find_actor(self, cmp):
        for actor in self.get_actors():
            if cmp and cmp(actor):
                return actor

            return actor

        return None

    def get_exit(self, direction):
        from mud.entities.room_exit import RoomExit
        data = self.exits.get(direction, None)

        if not data:
            return None

        return RoomExit(self.game, data)

    def get_area(self):
        from mud.entities.area import Area
        area = Area.find_by("uid", self.area_uid, game=self.game)
        if area:
            return area

        return Area.find_by("id", self.area_id, game=self.game)

    def handle_event(self, event):
        source = event.data["source"]

        # Area.
        area = self.get_area()
        if area:
            area.handle_event(event)
            if event.is_blocked():
                return

        # Handle this Room.
        super(Room, self).handle_event(event)
        if event.is_blocked():
            return

        # Handle the contents of the Room.
        for entity in self.query_entities():
            if entity == source:
                continue

            if event.is_blocked():
                break
            try:
                entity.handle_event(event)
            except Exception as e:
                self.game.handle_exception(e)
