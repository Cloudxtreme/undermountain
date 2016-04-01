from utils.entity import Entity
import inspect


class GameEntity(Entity):
    """
    GAME ENTITY
    """
    COLLECTION_NAME = None
    COLLECTIONS_CHECKED = []

    def __repr__(self):
        return "<{} uid:{} name:{}>".format(
            self.__class__.__name__,
            self.uid,
            self.name,
        )

    def __init__(self, game, data=None):
        super(Entity, self).__setattr__('game', game)
        super(GameEntity, self).__init__(data)

    @classmethod
    def get_game(cls):
        from mud.game import Game

        caller = cls.get_caller()
        if type(caller) is Game:
            return caller
        return caller.game

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
    def check_game_collections(cls, game):
        if cls.COLLECTION_NAME is None:
            raise Exception("COLLECTION_NAME for {} must be defined".format(
                cls.__name__
            ))

        if cls.__name__ in cls.COLLECTIONS_CHECKED:
            return

        game.data[cls.COLLECTION_NAME] = []
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
        game.data[cls.COLLECTION_NAME + "_by_uid"][data["uid"]] = data

    @classmethod
    def deindex(cls, data, game=None):
        if game is None:
            game = cls.get_game()
        del game.data[cls.COLLECTION_NAME + "_by_uid"][data["uid"]]

    @classmethod
    def find_by_uid(cls, uid, game=None):
        if game is None:
            game = cls.get_game()

        data = game.data[cls.COLLECTION_NAME + "_by_uid"].get(uid, None)

        if data:
            return cls(game, data)

        return None

    @classmethod
    def query(cls, game=None):
        if game is None:
            game = cls.get_game()

        cls.check_game_collections(game)

        return tuple(game.data[cls.COLLECTION_NAME])
