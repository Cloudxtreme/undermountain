from utils.entity import Entity
from mud.mixins.get_game import GetGame
import inspect


class GameEntity(Entity, GetGame):
    """
    GAME ENTITY
    """
    COLLECTION_NAME = None
    COLLECTIONS_CHECKED = []

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
        game.data[cls.COLLECTION_NAME + "_by_id"] = {}
        game.data[cls.COLLECTION_NAME + "_by_uid"] = {}

        cls.COLLECTIONS_CHECKED.append(cls.__name__)

    @classmethod
    def add(cls, data, game=None):
        """
        Create an Area in the Game.
        """
        if game is None:
            game = cls.get_game()
        cls.check_game_collections(game)

        game.data[cls.COLLECTION_NAME].append(data)

        cls.index(data, game)

    @classmethod
    def remove(cls, data, game=None):
        """
        Remove an Area from the Game.
        """
        if game is None:
            game = cls.get_game()

        cls.check_game_collections(game)

        cls.deindex(data, game)

        game.data[cls.COLLECTION_NAME].remove(data)

    @classmethod
    def index(cls, data, game=None):
        if game is None:
            game = cls.get_game()

        by_id = game.data[cls.COLLECTION_NAME + "_by_id"]
        id = data.get("id", None)
        if id:
            if not id in by_id:
                by_id[id] = []
            by_id[id].append(data)

        uid = data.get("uid", None)
        if uid:
            game.data[cls.COLLECTION_NAME + "_by_uid"][uid] = data

    @classmethod
    def deindex(cls, data, game=None):
        if game is None:
            game = cls.get_game()

        uid = data.get("uid", None)
        if uid:
            del game.data[cls.COLLECTION_NAME + "_by_uid"][data["uid"]]

        id = data.get("id", None)
        if id:
            by_id = game.data[cls.COLLECTION_NAME + "_by_id"][id]
            by_id.remove(self)
            if not by_id:
                del game.data[cls.COLLECTION_NAME + "_by_id"][id]

    @classmethod
    def wrap(cls, game, data):
        if data is None:
            return None

        # Do not recursively wrap.
        if type(data) is list:
            return [cls(game, item) for item in data]

        return cls(game, data)

    @classmethod
    def query_by_id(cls, id, game=None):
        if game is None:
            game = cls.get_game()

        data = game.data[cls.COLLECTION_NAME + "_by_id"].get(id, None)

        return cls.wrap(game, data)

    @classmethod
    def get_by_uid(cls, uid, game=None):
        if game is None:
            game = cls.get_game()

        data = game.data[cls.COLLECTION_NAME + "_by_uid"].get(uid, None)

        return cls.wrap(game, data)

    @classmethod
    def query(cls, game=None):
        if game is None:
            game = cls.get_game()

        cls.check_game_collections(game)

        return cls.wrap(game, game.data[cls.COLLECTION_NAME])
