from gevent import Greenlet
import gevent


class World(Greenlet):
    """
    WORLD
    Container for all Entities that make up the Game, like a chessboard filled
    with pieces that the Engine controls.
    """
    def __init__(self, engine):
        super(World, self).__init__()
        self.engine = engine
        self.data = {}  # Main memory core, reference relationships by ID only.

        from mud.entities.area import Area
        westbridge = {
            "uid": "zxc321",
            "id": "westbridge",
            "name": "Westbridge",
            "level_min": 1,
            "level_max": 10,
        }
        Area.create(westbridge)

        """
        The Temple of Life [LAW] [SAFE] [NOLOOT] (Westbridge) (cityst) [Room 3001]

        [Exits: north east south west]   [Doors: none]   [Secret: none]
             An old piece of paper lies on the floor.
        [.......L....] Hollywood Hogan is here, looking out for Sting.
        """

        from mud.entities.actor import Actor
        hogan = {
            "uid": "jahsdf1234",
            "id": "hogan",
            "area_id": "westbridge",
            "full_id": "westbridge:hogan",
            "name": "Hollywood Hogan",
            "room_string": "Hollywood Hogan is here, looking out for Sting.",
            "room_id": "westbridge:3001",
            "room_uid": "abc123",
            "effects": [
                {
                    "uid": "kjahsdkjhs7214",
                    "id": "shockshield",
                    "duration": 100,
                }
            ],
        }
        Actor.create(hogan)

        from mud.entities.room import Room
        temple_of_life = {
            "uid": "abc123",
            "id": "3001",
            "area_id": "westbridge",
            "full_id": "westbridge:3001",  # generated
            "flags": ["city", "indoor", "law", "safe", "noloot"],
            "name": "The Temple of Life",
            "description": [
                "This is the interior of a large white marble temple.  A pipe organ",
                "plays in the background as people sing a hymn of peacefulness.  A",
                "priest up front tells the story of the forces of the realms, be it Life,",
                "the force that gives breath and a heartbeat, and Death, the force that",
                "steals these gifts away.  There is a guard standing watch, keeping the",
                "peace.  To the south is the Temple Square and to the west is the donation",
                "room.  To the east is the City Morgue and a newer section of Main Street",
                "heads off to the north.",
            ],
            "exits": {
                "north": { "id": "westbridge:3001", "uid": "abc123" },
                "east": { "id": "westbridge:3001", "uid": "abc123" },
                "south": { "id": "westbridge:3001", "uid": "abc123" },
                "west": { "id": "westbridge:3001", "uid": "abc123" },
                "up": { "id": "westbridge:3001", "uid": "abc123" },
                "down": { "id": "westbridge:3001", "uid": "abc123" },
            },
            "actors": [
                {
                    "uid": "jahsdf1234"
                }
            ]
        }
        Room.create(temple_of_life)
