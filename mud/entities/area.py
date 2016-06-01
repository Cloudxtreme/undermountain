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
            return area

    def add_children(self):
        from mud.entities.room import Room
        for room_vnum, room in self.data["rooms"].items():
            room["id"] = room_vnum
            print(room)
            Room.add(room, game=self.game)

    def remove_children(self):
        print("GONNA DEHYDRATE DATA")
        print(len(self.data["rooms"]))
