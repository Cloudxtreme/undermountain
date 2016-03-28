from mud.entities.actor import Actor
import json
import re


class Character(Actor):
    """
    CHARACTER
    An Actor that can be controlled by a Player.
    """
    COLLECTION_NAME = 'characters'

    def format_room_name_for(self, other):
        # FIXME handle fighting
        output = self.name if other.can_see(self) else "Someone"

        if self.title:
            output += " " + self.title

        return output

    @classmethod
    def get_clean_name(self, name):
        name = name.strip()

        if not re.match("^[a-zA-Z]+$", name):
            return None

        name = name.lower().title()
        return name

    @classmethod
    def get_file_path(cls, uid):
        game = cls.get_game()
        env = game.get_environment()

        path = "{}/{}/{}".format(
            env.folder,
            cls.COLLECTION_NAME,
            uid,
        )
        return path

    @classmethod
    def get_from_file(cls, uid):
        game = cls.get_game()
        path = cls.get_file_path(uid)

        try:
            with open(path, "r") as fh:
                data = json.loads(fh.read())
                data["uid"] = uid
                return data
        except IOError:
            pass

        return None

    @classmethod
    def save_to_file(cls, data):
        data = dict(data)

        uid = data.get('uid', None)
        path = cls.get_file_path(uid)

        try:
            with open(path, "w") as fh:
                del data["uid"]
                return fh.write(json.dumps(data))
        except IOError:
            pass

        return None
