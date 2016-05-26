from gevent import Greenlet
from settings.servers import SERVER_CLASSES
from settings.managers import MANAGER_CLASSES
import gevent
import sys
import traceback


class Game(Greenlet):
    SHUTDOWN_FILENAME = 'SHUTDOWN'
    REBOOT_FILENAME = 'REBOOT'

    """
    GAME
    The single process that runs the game.
    """
    def handle_exception(self, *args, **kwargs):
        exc_type, exc_value, exc_traceback = sys.exc_info()

        message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        message = message.replace("{", "{{")
        print(message)
        self.wiznet("exception", message)

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

    def query_connections(self):
        for connection in self.connections:
            yield connection

    def add_connection(self, connection):
        self.connections.append(connection)

    def remove_connection(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)

    # TODO MOVE THIS TO CHARACTER MODEL
    def find_character(self, *args, **kwargs):
        for result in self.query_characters(*args, **kwargs):
            return result
        return None

    # TODO MOVE THIS TO CHARACTER MODEL
    def query_characters(self, func=None, name_like=None, visible_to=None):
        for connection in self.connections:
            if not connection.is_playing():
                continue

            actor = connection.get_actor()

            if not actor:
                continue

            if func is not None and not func(actor):
                continue

            if name_like is not None and not actor.name_like(name_like):
                continue

            if visible_to is not None and not visible_to.can_see(actor):
                continue

            yield actor

    def get_actor_connection(self, actor=None, actor_id=None, exclude=None):
        for connection in self.connections:
            if connection == exclude:
                continue

            if actor and connection.actor == actor:
                return connection

            if actor_id and connection.actor and connection.actor.id == actor_id:
                return connection

        return None

    def get_unique_connection_id(self):
        self.unique_connection_id += 1
        return self.unique_connection_id

    def __init__(self, environment, *args, **kwargs):
        """
        Instantiate an Engine for an Environment.
        """
        super(Game, self).__init__(*args, **kwargs)
        self.environment = environment
        self.processes = []
        self.connections = []
        self.unique_connection_id = 0

        self.data = {}  # Main memory core, reference relationships by ID only.

        from mud.entities.area import Area
        westbridge = {
            "uid": "zxc321",
            "id": "westbridge",
            "name": "Westbridge",
            "level_min": 1,
            "level_max": 10,
            "triggers": [
                {"type": "entered", "code": """
tell(actor, "Area aware of your entered")
                """},
            ]
        }
        Area.add(westbridge, self)

        from mud.entities.actor import Actor
        hogan = {
            "uid": "jahsdf1234",
            "id": "westbridge:hagon",
            "area_id": "westbridge",
            "area_uid": "zxc321",
            "full_id": "westbridge:hagon",
            "keywords": ["hurlywood", "hagon"],
            "name": "Hurlywood Hagon",
            "room_name": "Hurlywood Hagon is here, looking out for Styng.",
            "room_id": "westbridge:3001",
            "room_uid": "abc123",
            "effects": [
                {
                    "uid": "kjahsdkjhs7214",
                    "id": "shockshield",
                    "duration": 100,
                },
            ],
            "triggers": [
                {"type": "entered", "async": True, "code": """
say("Hello {}!".format(randint(1, 10)))
tell(actor, "Heyaaaa")
tell("Kelemv", "Heyaaaa")
say("Say {cnote{m or {chagon{m for some more testing.", trigger=False)
wait(1)
say("I waited to say something.")
raise Exception("Testing")
"""},
                {"type": "saying", "code": """
if "hagon" in message:
    say("I blocked an attempt to say my name.")
    block()
"""}
            ]
        }
        Actor.add(hogan, self)

        from mud.entities.object import Object
        note = {
            "uid": "note1234",
            "id": "note",
            "room_id": "westbridge:3001",
            "room_uid": "abc123",
            "name": "An old note",
            "room_name": "An old piece of paper lies on the floor.",
            "triggers": [
                {"type": "entered", "code": """
say("Testing out oprogs.")
                """},
                {"type": "saying", "code": """
if "note" in message:
    say("I blocked an attempt to say my name.")
    block()
"""}
            ]
        }
        Object.add(note, self)

        from mud.entities.room import Room
        temple_of_life = {
            "uid": "abc123",
            "id": "westbridge:3001",
            "area_id": "westbridge",
            "area_uid": "zxc321",
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
                "south": { "room_id": "westbridge:3005", "room_uid": "xyz321" },
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
            "triggers": [
                {"type": "entered", "code": """
tell(actor, "Room aware of your entered")
                """},
            ]
        }
        Room.add(temple_of_life, self)

        hwi = {
            "uid": "hwi123",
            "id": "westbridge:3008",
            "area_id": "westbridge",
            "flags": ["city", "indoor", "law", "safe", "noloot"],
            "name": "Healing Wound Inn",
            "description": [
                "People of all kinds can normally be found resting within this",
                "large inn.  Most will sit around the healer, telling stories about",
                "their last adventure. The owner of the inn, a former adventurer",
                "himself, stands here giving and selling spells. A large featherbed",
                "rests here, just big enough for two. There is a large sofa against",
                "the east wall and a huge pool with bubbles that looks like ten men",
                "could fit in it.  A {gsign{x hangs on the wall.",
            ],
            "exits": {
                "west": { "room_id": "westbridge:3005", "room_uid": "xyz321" },
            },
        }
        Room.add(hwi, self)

        temple_square = {
            "uid": "xyz321",
            "id": "westbridge:3005",
            "area_id": "westbridge",
            "area_uid": "zxc321",
            "flags": ["city", "outdoor", "law", "noloot"],
            "name": "Temple Square",
            "description": [
                "Here is the middle of the Temple Square.  To the north, huge marble",
                "steps lead up to the temple gate.  The entrance to a large cathedral",
                "is to the west and The Healing Wound Inn is just east of here.  A few",
                "large cracks in the ground can be seen.",
            ],
            "exits": {
                "up": { "room_id": "westbridge:3005", "room_uid": "xyz321" },
                "north": { "room_id": "westbridge:3001", "room_uid": "abc123" },
                "east": { "room_id": "westbridge:3008", "room_uid": "hwi123" },
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
        Room.add(temple_square, self)

        from utils.time import Time
        Time.tick('game_start')

        # rooms
        for x in range(1, 100000):
            created_id = "room:" + str(x)
            created = dict(temple_square)
            created["uid"] = created_id
            created["id"] = created_id
            Room.add(created, self)

        # mobs
        for x in range(1, 100000):
            created_id = "actor:" + str(x)
            created = dict(hogan)
            created["uid"] = created_id
            created["id"] = created_id
            created["room_uid"] = "room:3"
            created["room_id"] = "room:3"
            Actor.add(created, self)

        Time.tock('game_start')

    def echo(self, message, role=None):
        print("ROLE", role)

        if type(message) is list:
            message = ''.join(message)
            self.echo(message, role=role)
            return

        for actor in self.query_characters():
            if role is not None:
                if not actor.has_role(role):
                    continue

            actor.echo(message)

    def _run(self):
        """
        Start the Engine.
        """
        import os

        self.running = True

        self.create_processes()

        while self.running:

            if os.path.isfile(self.REBOOT_FILENAME):
                try:
                    os.remove(self.REBOOT_FILENAME)
                except Exception:
                    pass
                self.echo("Rebooting..")
                break

            if os.path.isfile(self.SHUTDOWN_FILENAME):
                try:
                    os.remove(self.SHUTDOWN_FILENAME)
                except Exception:
                    pass
                self.echo("Shutting down..")
                break

            gevent.sleep(0.5)

        self.shutdown_processes()

    def shutdown_processes(self):
        for connection in self.connections:
            connection.destroy()

    def create_processes(self):
        for process_class in SERVER_CLASSES + MANAGER_CLASSES:
            process = process_class(self)
            self.processes.append(process)
            gevent.spawn(process.start)

    def get_environment(self):
        return self.environment

    def wiznet(self, channel, message):
        self.echo("{{Y-->{{x ({}{{x) {}{{x".format(
            channel,
            message,
        ), role="admin")
