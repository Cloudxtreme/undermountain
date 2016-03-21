from mud.entity import Entity
from mud.world import World
import inspect


class WorldEntity(Entity):
    """
    WORLD ENTITY
    """
    COLLECTION_NAME = None
    COLLECTIONS_CHECKED = []

    def __init__(self, world, data=None):
        super(Entity, self).__setattr__('world', world)
        super(WorldEntity, self).__init__(data)

    @classmethod
    def get_world(cls):
        caller = cls.get_caller()
        if type(caller) is World:
            return caller
        return caller.world

    @classmethod
    def uses_world(cls, func):
        world = cls.get_world()
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapped

    @classmethod
    def get_caller(cls):
        try:
            for frame in inspect.stack():
                obj = frame[0].f_locals.get('self', None)
                if obj is not None:
                    return obj

        except KeyError:
            return None

        return None

    @classmethod
    def check_world_collections(cls, world):
        if cls.COLLECTION_NAME is None:
            raise Exception("COLLECTION_NAME for {} must be defined".format(
                cls.__name__
            ))

        if cls.__name__ in cls.COLLECTIONS_CHECKED:
            return

        world.data[cls.COLLECTION_NAME] = []
        world.data[cls.COLLECTION_NAME + '_by_uid'] = {}

        cls.COLLECTIONS_CHECKED.append(cls.__name__)

    @classmethod
    def create(cls, data, world=None):
        """
        Create an Area in the World.
        """
        if world is None:
            world = cls.get_world()
        cls.check_world_collections(world)

        world.data[cls.COLLECTION_NAME].append(data)
        print("Appended ID:{} to {}".format(
            data['id'],
            cls.COLLECTION_NAME
        ))

        cls.index(data, world)

    @classmethod
    def destroy(cls, data, world=None):
        """
        Remove an Area from the World.
        """
        if world is None:
            world = cls.get_world()

        cls.check_world_collections(world)

        cls.deindex(data, world)

        world.data[cls.COLLECTION_NAME].remove(data)

    @classmethod
    def index(cls, data, world):
        if world is None:
            world = cls.get_world()
        world.data[cls.COLLECTION_NAME + '_by_uid'][data['uid']] = data

    @classmethod
    def deindex(cls, data, world):
        if world is None:
            world = cls.get_world()
        del world.data[cls.COLLECTION_NAME + '_by_uid'][data['uid']]

    @classmethod
    def get_by_uid(cls, uid, world=None):
        if world is None:
            world = cls.get_world()
        return cls(world, world.data[cls.COLLECTION_NAME + '_by_uid'][uid])
