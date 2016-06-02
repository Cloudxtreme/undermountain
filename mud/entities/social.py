from mud.game_entity import GameEntity
import json


class Social(GameEntity):
    """
    SOCIAL
    An action that you can perform that's built into the game.
    """
    COLLECTION_NAME = "socials"
    STRING_INDEXES = ["name"]

    @classmethod
    def get_file_path(cls, uid, game):
        env = game.get_environment()

        path = "{}/{}/{}.json".format(
            env.folder,
            cls.COLLECTION_NAME,
            uid,
        )
        return path

    @classmethod
    def load_from_file(cls, uid, game):
        path = cls.get_file_path(uid=uid, game=game)
        with open(path, "r") as input_file:
            social = json.loads(input_file.read())
            social["name"] = uid
            return social

    @classmethod
    def query_available_uids(cls, game):
        import glob
        env = game.get_environment()
        path = "{}/{}/*.json".format(
            env.folder,
            cls.COLLECTION_NAME
        )
        for full_path in glob.iglob(path):
            parts = full_path.split("/")
            filename = parts[-1]
            yield filename.split(".json")[0]
