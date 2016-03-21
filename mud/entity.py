class Entity(object):
    def __init__(self, data):
        super(Entity, self).__setattr__("data", data)

    def __setattr__(self, key, value):
        self.data[key] = value

    def __getattr__(self, key):
        return self.data.get(key)

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __getitem(self, key):
        return self.__getattr__(key)

    def set(self, key, value):
        self.__setattr__(key, value)

    def get(self, key, default=None):
        return self.data.get(key, default)
