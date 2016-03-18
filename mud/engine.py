from gevent import Greenlet
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

    def _run(self):
        """
        Start the Engine.
        """
        self.running = True
        while self.running:
            print("Tick")
            gevent.sleep(1.0)
