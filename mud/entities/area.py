from mud.game_entity import GameEntity


class Area(GameEntity):
    """
    AREA
    A container that holds a grouping of areas, Actors, etc.
    """
    COLLECTION_NAME = "areas"
    STRING_INDEXES = ["name"]
