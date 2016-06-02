class Entity(object):
    def __init__(self, data=None):
        if not data:
            data = {}
        super(Entity, self).__setattr__("data", data)

    def __eq__(self, other):
        if other is None or not hasattr(other, "get"):
            return False

        return self.get("uid") == other.get("uid")

    def __ne__(self, other):
        return not self.__eq__(other)

    def __setattr__(self, key, value):
        self.data[key] = value

    def __delattr__(self, key):
        if key in self.data:
            del self.data[key]

    def __getattr__(self, key):
        return self.data.get(key, None)

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __getitem__(self, key):
        return self.__getattr__(key)

    def set(self, key, value):
        self.__setattr__(key, value)

    def get(self, key, default=None):
        return self.data.get(key, default)
