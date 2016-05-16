from mud.room_entity import RoomEntity


class Object(RoomEntity):
    """
    OBJECT
    A statue, bag, sword, or other "thing"in the room.
    """
    COLLECTION_NAME = 'objects'

    def can_see(self, other):
        # FIXME check for flags
        return True
