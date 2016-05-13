from utils.entity import Entity


class GameEntity(Entity):
    """
    GAME ENTITY
    """
    COLLECTION_NAME = None
    COLLECTIONS_CHECKED = []

    UNIQUE_INDEXES = ['uid']
    STRING_INDEXES = ['keywords']
    INDEXES = ['id']

    def __repr__(self):
        return "<{} uid:{} name:{} python:{}>".format(
            self.__class__.__name__,
            self.uid,
            self.name,
            id(self),
        )

    def __init__(self, game, data=None):
        super(Entity, self).__setattr__('game', game)
        super(GameEntity, self).__init__(data)

    @classmethod
    def check_game_collections(cls, game):
        if cls.COLLECTION_NAME is None:
            raise Exception("COLLECTION_NAME for {} must be defined".format(
                cls.__name__
            ))

        if cls.__name__ in cls.COLLECTIONS_CHECKED:
            return

        game.data[cls.COLLECTION_NAME] = []

        for key in cls.UNIQUE_INDEXES + cls.STRING_INDEXES:
            game.data[cls.COLLECTION_NAME + '_by_' + key] = {}

        for key in cls.INDEXES:
            game.data[cls.COLLECTION_NAME + '_by_' + key] = []

        # TODO HANDLE STRING INDEXES

        cls.COLLECTIONS_CHECKED.append(cls.__name__)

    @classmethod
    def add(cls, data, game):
        """
        Create an Area in the Game.
        """
        cls.check_game_collections(game)

        game.data[cls.COLLECTION_NAME].append(data)

        cls.index(data, game)

    @classmethod
    def remove(cls, data, game=None):
        """
        Remove an Area from the Game.
        """
        cls.check_game_collections(game)

        cls.deindex(data, game)

        game.data[cls.COLLECTION_NAME].remove(data)

    @classmethod
    def index(cls, data, game):

        for key in cls.UNIQUE_INDEXES:
            full_key = cls.COLLECTION_NAME + '_by_' + key

            # Check for uniqueness naming collision.
            if data.get(key, "") in game.data:
                raise Exception("{} with key '{}' collision".format(
                    cls.__name__,
                    key,
                ))

            value = data.get(key, "")
            print("INDEXING {} {} '{}'".format(cls.__name__, full_key, value))
            # TODO HANDLE BLANKS
            game.data[full_key][value] = data

        for key in cls.INDEXES:
            full_key = cls.COLLECTION_NAME + '_by_' + key

            game.data[full_key].append(data)

        # TODO String indexes for searching startswith/contains.

    @classmethod
    def deindex(cls, data, game):

        for key in cls.UNIQUE_INDEXES:
            full_key = cls.COLLECTION_NAME + '_by_' + key
            value = data.get(key, "")
            # TODO HANDLE BLANKS
            del game.data[full_key][data.get(value)]

        for key in cls.INDEXES:
            full_key = cls.COLLECTION_NAME + '_by_' + key
            game.data[full_key].remove(data)

        # TODO String indexes for searching startswith/contains.

    @classmethod
    def query_by_id(cls, id, game):
        return cls.query_by("id", id, game)

    @classmethod
    def get_by_uid(cls, uid, game):
        full_key = cls.COLLECTION_NAME + "_by_uid"
        result = game.data[full_key].get(uid, None)
        if not result:
            return None
        return cls(game, result)

    @classmethod
    def query(cls, game):
        cls.check_game_collections(game)

        # TODO CHECK INDEX EXISTS?
        for result in game.data[cls.COLLECTION_NAME]:
            yield cls(game, result)

    @classmethod
    def query_by(cls, field, value, game):
        cls.check_game_collections(game)

        # TODO check index exists
        full_key = cls.COLLECTION_NAME + '_by_' + field
        for entry in game.data[full_key]:
            if entry.get(field, None) == value:
                yield cls(game, entry)

