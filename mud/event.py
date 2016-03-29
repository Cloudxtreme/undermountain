class Event(object):
    def __init__(self, name, data=None):
        self.blocked = False
        self.name = name
        self.data = data if data else {}

    def unblock(self):
        self.blocked = False

    def block(self):
        self.blocked = True

    def is_blocked(self):
        return self.blocked
