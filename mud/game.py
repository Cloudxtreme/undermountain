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

    def log(self, *args, **kwargs):
        print(*args, **kwargs)

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

        # FIXME put somewhere better, like an AreaManager
        for area_name in Area.query_available_uids(game=self):
            area_data = Area.load_from_file(area_name, game=self)
            Area.add(area_data, game=self)
            self.log("Loaded area '{}' with {} rooms".format(
                area_name,
                len(area_data["rooms"])
            ))

        from mud.entities.social import Social

        # FIXME put somewhere better, like an AreaManager
        for social_name in Social.query_available_uids(game=self):
            social = Social.load_from_file(social_name, game=self)
            Social.add(social, game=self)
            self.log("Loaded social '{}'".format(social_name))


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
