from mud.game_entity import GameEntity
import json


class Area(GameEntity):
    """
    AREA
    A container that holds a grouping of areas, Actors, etc.
    """
    COLLECTION_NAME = "areas"
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
            area = json.loads(input_file.read())
            area["id"] = uid
            for room_id, room in area["rooms"].items():
                room["area_id"] = uid
            return area

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

    def add_children(self):
        from mud.entities.room import Room
        for room_vnum, room in self.data["rooms"].items():
            room["id"] = room_vnum
            Room.add(room, game=self.game)

    def remove_children(self):
        pass
