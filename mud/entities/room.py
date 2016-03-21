from mud.world_entity import WorldEntity


class Room(WorldEntity):
    """
    ROOM
    A container that Actors, Objects, and general "things" can be in.
    """
    COLLECTION_NAME = 'rooms'
