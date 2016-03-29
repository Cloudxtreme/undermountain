from mud.game_entity import GameEntity


class Room(GameEntity):
    """
    ROOM
    A container that Actors, Objects, and general "things" can be in.
    """
    COLLECTION_NAME = 'rooms'

    def get_actors(self, exclude=None):
        """
        Get all the Actors in this Room.
        """
        from mud.entities.actor import Actor
        # FIXME use some kind of reusable filtering function
        actors = []
        for actor in Actor.query_by_room_uid(self.uid, game=self.game):
            if actor == exclude:
                continue
            actors.append(actor)
        return actors

    def get_exit(self, direction):
        from mud.entities.room_exit import RoomExit
        data = self.exits.get(direction, None)
        print(self.exits, direction)

        if not data:
            return None

        return RoomExit(self.game, data)
