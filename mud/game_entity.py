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
    def get_by_uid(cls, *args, **kwargs):
        return cls.find_by_uid(*args, **kwargs)

    @classmethod
    def find_by_uid(cls, uid, game):
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

        if not full_key in game.data:
            raise Exception("Field '{}' for '{}' not indexed and cannot be queries".format(
                field,
                cls.__name__,
            ))

        index = game.data[full_key]

        if value in index:
            records = index[value]

            if field in cls.UNIQUE_INDEXES:
                yield records

            elif field in cls.STRING_INDEXES:
                # FIXME handle string indexes
                raise Exception("String indexes not yet handled.")

            elif field in cls.INDEXES:
                for record in records:
                    yield record

            else:
                raise Exception("'{}' index for '{}' GameEntities not yet implemented".format(
                    field,
                    cls.__name__,
                ))

    @classmethod
    def find_by(cls, *args, **kwargs):
        for entry in cls.query_by(*args, **kwargs):
            return entry

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

    def can_see(self, other):
        return True

    def tell(self, raw_target, message):
        """
        Tell another player a message.

        tell <name> <message>
        """
        from mud.entities.actor import Actor
        from mud.entities.character import Character

        target = None

        if isinstance(raw_target, Actor):
            target = raw_target
        elif raw_target:
            def match_tell_player(other):
                return other.name_like(raw_target) and \
                    self.can_see(other)
            target = Character.find(func=match_tell_player, game=self.game)

        if not target:
            self.echo("Target not found.")
            return

        self.echo("{{gYou tell {}{{g '{{G{}{{g'{{x".format(
            target.format_name_to(self),
            message
        ))

        if self != target:
            target.echo("{{g{}{{g tells you '{{G{}{{g'{{x".format(
                self.format_name_to(target),
                message
            ))

    def format_name_to(self, other):
        return self.get("name", "Something") if other.can_see(self) else "Something"

    def echo(self, *args, **kwargs):
        pass

    def execute_subroutine(self, compiled, context):
        try:
            exec(compiled, context, context)
        except Exception as e:
            self.game.handle_exception(e)

    def handle_wait_in_blockable_event(self, event):
        raise Exception("You cannot use 'wait' in blockable event")

    def handle_event(self, event):
        import random
        import time
        import gevent

        context = {}
        context.update(event.data)
        context.update({
            "other": event.data["source"],
            "source": event.data["source"],
            "actor": event.data["source"],

            "say": self.say,
            "tell": self.tell,
            "self": self,

            "block": event.block,

            "randint": random.randint,
            "random": random.randint,
        })

        for trigger in self.query_triggers_by_type(event.type):

            # Only compile on-demand.
            compiled = trigger.get("compiled", None)
            if compiled is None:
                compiled = compile(trigger["code"], self.uid + ':' + event.type, "exec")
                trigger["compiled"] = compiled

            try:
                if event.blockable:
                    context.update({
                        "wait": self.handle_wait_in_blockable_event
                    })
                    exec(compiled, context, context)
                else:
                    context.update({
                        "wait": time.sleep
                    })
                    thread = gevent.spawn(self.execute_subroutine, compiled, context)

            except Exception as e:
                self.game.handle_exception(e)
