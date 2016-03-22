class Environment(object):
    """
    ENVIRONMENT
    A group of settings identified by a single name, such as 'live' or 'dev'
    """
    @classmethod
    def get(cls, id):
        """
        Get an Environment by its ID.
        """
        return Environment()

    def __init__(self):
        """
        FIXME Make this load from a real place.
        """
        self.id = 'test'
        self.settings = {
            "servers": {
                "telnet": {
                    "port": 4200
                }
            }
        }
        self.folder = 'data/live'
