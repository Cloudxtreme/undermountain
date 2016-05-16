from utils.entity import Entity


class GameEntity(Entity):
    """
    GAME ENTITY
    """
    COLLECTION_NAME = None
    COLLECTIONS_CHECKED = set()

    UNIQUE_INDEXES = ['uid']
    STRING_INDEXES = ['keywords']
    INDEXES = ['id']

    @classmethod
    def query_index_fields(cls):
        return cls.UNIQUE_INDEXES + cls.STRING_INDEXES + cls.INDEXES

    # FIXME make this a decorator, the index/deindex
    def __delattr__(self, key, value):
        indexes = self.query_index_fields()
        if key in indexes:
            self.deindex()

        super(GameEntity, self).__setattr__(key, value)

        if key in indexes:
            self.index()

    def __setattr__(self, key, value):
        indexes = self.query_index_fields()
        if key in indexes:
            self.deindex()

        super(GameEntity, self).__setattr__(key, value)

        if key in indexes:
            self.index()

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

        for key in cls.query_index_fields():
            game.data[cls.COLLECTION_NAME + '_by_' + key] = {}

        # TODO HANDLE STRING INDEXES

        cls.COLLECTIONS_CHECKED.add(cls.__name__)

    @classmethod
    def add(cls, data, game):
        """
        Add this Entity to the Game.
        """
        entity = cls(game, data)

        cls.check_game_collections(game)

        game.data[cls.COLLECTION_NAME].append(entity)

        entity.index()

        return entity

    def remove(self):
        """
        Remove this Entity from the Game.
        """
        self.check_game_collections(self.game)

        self.deindex()

        self.game.data[self.COLLECTION_NAME].remove(self)

    def index(self):

        for key in self.UNIQUE_INDEXES:
            full_key = self.COLLECTION_NAME + '_by_' + key

            # Check for uniqueness naming collision.
            if self.get(key, "") in self.game.data:
                raise Exception("{} with key '{}' collision".format(
                    self.__name__,
                    key,
                ))

            value = self.get(key, "")
            # TODO HANDLE BLANKS
            self.game.data[full_key][value] = self

        for key in self.INDEXES:
            full_key = self.COLLECTION_NAME + '_by_' + key
            value = self.get(key, "")

            if value not in self.game.data[full_key]:
                self.game.data[full_key][value] = []

            self.game.data[full_key][value].append(self)

        # TODO String indexes for searching startswith/contains.

    def deindex(self):
        for key in self.UNIQUE_INDEXES:
            full_key = self.COLLECTION_NAME + '_by_' + key
            value = self.get(key, "")
            # TODO HANDLE BLANKS
            del self.game.data[full_key][value]

        for key in self.INDEXES:
            full_key = self.COLLECTION_NAME + '_by_' + key
            value = self.get(key, "")
            self.game.data[full_key][value].remove(self)

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
        return result

    @classmethod
    def query(cls, game):
        cls.check_game_collections(game)

        # TODO CHECK INDEX EXISTS?
        for result in game.data[cls.COLLECTION_NAME]:
            yield result

    @classmethod
    def query_by(cls, field, value, game):
        cls.check_game_collections(game)

        # TODO check index exists
        full_key = cls.COLLECTION_NAME + '_by_' + field
        if value in game.data[full_key]:
            for entry in game.data[full_key][value]:
                yield entry

    def query_triggers_by_type(self, event_type):
        for trigger in self.get("triggers", []):
            if trigger["type"] == event_type:
                yield trigger

    def nyi(self, thing=None):
        message = "'{}' not implemented for '{}' entities".format(
            thing,
            self.__class__.__name__
        )
        raise Exception(message)

    def say(self, *args, **kwargs):
        self.nyi("say")

    def format_name_to(self, other):
        return self.get("name", "Something") if other.can_see(self) else "Something"

    def tell(self, *args, **kwargs):
        self.nyi("say")

    def echo(self, *args, **kwargs):
        pass

    def handle_event(self, event):
        import random

        context = {}
        context.update(event.data)
        context.update({
            "actor": event.data["source"],
            "say": self.say,
            "tell": self.tell,
            "data": event.data,
            "block": event.block,
            "randint": random.randint,
        })

        for trigger in self.query_triggers_by_type(event.type):

            # Only compile on-demand.
            compiled = trigger.get("compiled", None)
            if compiled is None:
                compiled = compile(trigger["code"], self.uid + ':' + event.type, "exec")
                trigger["compiled"] = compiled

            try:
                exec(compiled, context, context)

            except Exception, e:
                print("FIXME: better exception handling of this failure")
                self.game.handle_exception(e)
