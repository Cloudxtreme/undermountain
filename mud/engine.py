from gevent import Greenlet
from mud.world import World
import gevent


class Engine(Greenlet):
    """
    ENGINE
    The interface between Players' network connectivity and the World.
    """

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

    def __init__(self, environment, *args, **kwargs):
        """
        Instantiate an Engine for an Environment.
        """
        super(Engine, self).__init__(*args, **kwargs)
        self.environment = environment

    def create_world(self):
        """
        Start the World.
        """
        self.world = World(self)

    def _run(self):
        """
        Start the Engine.
        """
        self.running = True

        self.create_world()
        self.world.start()

        while self.running:
            gevent.sleep(1.0)

        self.world.stop()
