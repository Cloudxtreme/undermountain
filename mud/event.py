class Event(object):
    def __init__(self, type, data=None, blockable=False):
        self.blocked = False
        self.blockable = blockable
        self.type = type
        self.data = data if data else {}

    def unblock(self):
        if not self.blockable:
            raise Exception("Event unblocked despite not being set blockable.")
        self.blocked = False

    def block(self):
        if not self.blockable:
            raise Exception("Event blocked despite not being set blockable.")
        self.blocked = True

    def is_blocked(self):
        return self.blocked
