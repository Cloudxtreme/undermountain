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
        actors = self.get_actors()

        for actor in actors:
            if cmp(actor):
                return actor

        return None

    def get_exit(self, direction):
        from mud.entities.room_exit import RoomExit
        data = self.exits.get(direction, None)

        if not data:
            return None

        return RoomExit(self.game, data)

    def handle_event(self, event):
        for actor in self.get_actors():
            if actor is self:
                continue

            if event.is_blocked():
                break
            try:
                # gevent.spawn(actor.handle_event, event)
                actor.handle_event(event)
            except Exception, e:
                self.game.handle_exception(e)
