class Event(object):
    def __init__(self, type, data=None, blockable=False):
        self.blocked = False
        self.type = type
        self.data = data if data else {}
        self.blockable = blockable

    def unblock(self):
        if not self.blockable:
            raise Exception("Cannot unblock non-blockable Event.")
        self.blocked = False

    def block(self):
        if not self.blockable:
            raise Exception("Cannot block non-blockable Event.")
        self.blocked = True

    def is_blocked(self):
        return self.blocked
