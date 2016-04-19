from gevent import Greenlet
from settings.servers import SERVER_CLASSES
import gevent
import sys
import traceback


class Game(Greenlet):
    """
    GAME
    The single process that runs the game.
    """
    def handle_exception(self, e):
        # TODO HANDLE PROPERLY
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  limit=2, file=sys.stdout)

    @classmethod
    def get_version(cls):
        """
        Get the current Engine version.
        """
        try:
            with open("VERSION", "r") as version_file:
                version = version_file.read().strip()
                return version
        except IOError:
            pass

        return None

    def add_connection(self, connection):
        self.connections.append(connection)

    def remove_connection(self, connection):
        self.connections.remove(connection)

    def get_characters(self):
        return [
            connection.actor
            for connection in self.connections
            if connection.actor
        ]

    def get_actor_connection(self, actor=None, actor_id=None, exclude=None):
        for connection in self.connections:
            if connection == exclude:
                continue

            if actor and connection.actor == actor:
                return connection

            if actor_id and connection.actor and connection.actor.id == actor_id:
                return connection

        return None

    def __init__(self, environment, *args, **kwargs):
        """
        Instantiate an Engine for an Environment.
        """
        super(Game, self).__init__(*args, **kwargs)
        self.environment = environment
        self.processes = []
        self.connections = []

        self.data = {}  # Main memory core, reference relationships by ID only.

        from mud.entities.area import Area
        westbridge = {
            "uid": "zxc321",
            "id": "westbridge",
            "name": "Westbridge",
            "level_min": 1,
            "level_max": 10,
        }
        Area.add(westbridge)

        from mud.entities.actor import Actor
        hogan = {
            "uid": "jahsdf1234",
            "id": "westbridge:hogan",
            "area_id": "westbridge",
            "full_id": "westbridge:hogan",
            "name": "Hollywood Hogan",
            "room_name": "Hollywood Hogan is here, looking out for Sting.",
            "room_id": "westbridge:3001",
            "room_uid": "abc123",
            "effects": [
                {
                    "uid": "kjahsdkjhs7214",
                    "id": "shockshield",
                    "duration": 100,
                },
            ],
        }
        Actor.add(hogan)

        from mud.entities.object import Object
        note = {
            "uid": "note1234",
            "id": "note",
            "room_id": "westbridge:3001",
            "room_uid": "abc123",
            "room_name": "An old piece of paper lies on the floor.",
        }
        Object.add(note)

        from mud.entities.room import Room
        temple_of_life = {
            "uid": "abc123",
            "id": "westbridge:3001",
            "area_id": "westbridge",
            "flags": ["city", "indoor", "law", "safe", "noloot"],
            "name": "The Temple of Life",
            "description": [
                "This is the interior of a large white marble temple.  A pipe organ",
                "plays in the background as people sing a hymn of peacefulness.  A",
                "priest up front tells the story of the forces of the realms, be it Life,",
                "the force that gives breath and a heartbeat, and Death, the force that",
                "steals these gifts away.  There is a guard standing watch, keeping the",
                "peace.  To the south is the Temple Square and to the west is the donation",
                "room.  To the east is the {RCity Morgue{x and a newer section of Main Street",
                "heads off to the north.",
            ],
            "exits": {
                "north": { "room_id": "westbridge:3005", "room_uid": "xyz321" },
                "east": { "room_id": "westbridge:3001", "room_uid": "abc123" },
                "south": { "room_id": "westbridge:3005", "room_uid": "xyz321" },
                "west": { "room_id": "westbridge:3001", "room_uid": "abc123" },
                "up": { "room_id": "westbridge:3001", "room_uid": "abc123" },
            },
            "objects": [
                {
                    "uid": "note1234",
                },
            ],
            "actors": [
                {
                    "uid": "jahsdf1234",
                },
            ],
        }
        Room.add(temple_of_life)

        temple_square = {
            "uid": "xyz321",
            "id": "westbridge:3005",
            "area_id": "westbridge",
            "flags": ["city", "outdoor", "law", "noloot"],
            "name": "Temple Square",
            "description": [
                "Here is the middle of the Temple Square.  To the north, huge marble",
                "steps lead up to the temple gate.  The entrance to a large cathedral",
                "is to the west and The Healing Wound Inn is just east of here.  A few",
                "large cracks in the ground can be seen.",
            ],
            "exits": {
                "north": { "room_id": "westbridge:3001", "room_uid": "abc123" },
                "east": { "room_id": "westbridge:3005", "room_uid": "xyz321" },
                "south": { "room_id": "westbridge:3001", "room_uid": "abc123" },
                "west": { "room_id": "westbridge:3005", "room_uid": "xyz321" },
                "up": { "room_id": "westbridge:3005", "room_uid": "xyz321" },
            },
            "objects": [
                {
                    "uid": "note1234",
                },
            ],
            "actors": [
                {
                    "uid": "jahsdf1234",
                },
            ],
        }
        Room.add(temple_square)

    def _run(self):
        """
        Start the Engine.
        """
        self.running = True

        self.create_processes()

        while self.running:
            gevent.sleep(1.0)

    def create_processes(self):
        for process_class in SERVER_CLASSES:
            process = process_class(self)
            self.processes.append(process)
            process.start()

    def get_environment(self):
        return self.environment
