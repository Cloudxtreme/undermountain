from mud.entities.actor import Actor
from mud.entities.room import Room
import json
import re


class Character(Actor):
    """
    CHARACTER
    An Actor that can be controlled by a Player.
    """
    COLLECTION_NAME = 'characters'

    def __init__(self, *args, **kwargs):
        super(Character, self).__init__(*args, **kwargs)

        if not self.class_id:
            # FIXME DEFAULTS
            self.class_id = 'vampire'

        if not self.race_id:
            self.race_id = 'human'

        if not self.gender_id:
            self.gender_id = 'male'

    def name_like(self, params):
        if type(params) is None:
            return False

        if type(params) is str or type(params) is unicode:
            params = tuple([params])
        elif type(params) is not tuple:
            params = tuple(params)

        if len(params) > 1:
            return False

        return self.name.lower().startswith(params[0].lower())

    def format_room_name_to(self, other):
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
    def get_file_path(cls, uid, game):
        env = game.get_environment()

        path = "{}/{}/{}".format(
            env.folder,
            cls.COLLECTION_NAME,
            uid,
        )
        return path

    @classmethod
    def get_from_file(cls, uid, game):
        path = cls.get_file_path(uid, game)

        try:
            with open(path, "r") as fh:
                data = json.loads(fh.read())
                data["id"] = uid
                data["uid"] = uid
                return data
        except IOError:
            pass
        except Exception as e:
            game.handle_exception(e)

        return None

    @classmethod
    def get_password_hash(cls, password):
        password = password.split()

        if not password:
            raise Exception("Blank password cannot be hashed.")

        # FIXME REPLACE THIS WITH A REAL HASH
        return password[0]

    def save(self):
        Character.save_to_file(self.data, game=self.game)

    @classmethod
    def save_to_file(cls, data, game):
        save_data = dict(data)

        uid = save_data.get('uid', None)
        path = cls.get_file_path(uid, game)

        try:
            with open(path, "w") as fh:
                del save_data["uid"]
                return fh.write(json.dumps(save_data))
        except IOError:
            pass
