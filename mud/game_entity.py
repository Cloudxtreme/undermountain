from utils.entity import Entity


class GameEntity(Entity):
    """
    GAME ENTITY
    """
    COLLECTION_NAME = None
    COLLECTIONS_CHECKED = set()

    UNIQUE_INDEXES = ['uid']
    STRING_INDEXES = []
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
    def get_unique_hash(cls):
        import random
        hash = random.getrandbits(128)
        return "%032x" % hash

    @classmethod
    def add(cls, data, game):
        """
        Add this Entity to the Game.
        """
        if not "uid" in data:
            data["uid"] = cls.get_unique_hash()

        entity = cls(game, data)

        cls.check_game_collections(game)

        game.data[cls.COLLECTION_NAME].append(entity)

        entity.index()
        entity.add_children()

        return entity

    def remove(self):
        """
        Remove this Entity from the Game.
        """
        self.check_game_collections(self.game)

        self.remove_children()
        self.deindex()

        self.game.data[self.COLLECTION_NAME].remove(self)

    def add_children(self):
        """
        Add the child entities into the game too.
        """
        pass

    def remove_children(self):
        """
        Remove the child entities out of the game too.
        """
        pass

    @classmethod
    def get_string_index_value_variations(cls, value):
        """
        Provide all of the combinations that make up the word.
        Returns a list ordered in highest value to lowest (length).
        """
        value = value.lower()
        variations = []

        for x in range(len(value), 0, -1):
            variation = value[0:x]
            variations.append(variation)

        return variations

    @classmethod
    def get_index_key(cls, key):
        return cls.COLLECTION_NAME + '_by_' + key

    @classmethod
    def get_game_index(cls, game, key):
        full_key = cls.get_index_key(key)
        index = game.data[full_key]
        return index

    @classmethod
    def unique_index_by(cls, key, value, record, game):
        if not value:
            return

        index = cls.get_game_index(game, key)

        # Check for uniqueness naming collision.
        if value in index:
            raise ValueError("{} with key '{}' collision for value '{}'".format(
                cls.__name__,
                key,
                value,
            ))

        index[value] = record

    @classmethod
    def normal_index_by(cls, key, value, record, game):
        if not value:
            return

        index = cls.get_game_index(game, key)

        if value not in index:
            index[value] = []

        index[value].append(record)

    @classmethod
    def string_index_by(cls, key, value, record, game):
        if not value:
            return

        index = cls.get_game_index(game, key)

        values = value
        if type(values) is str:
            values = values.split()

        for keyword in values:
            for variation in cls.get_string_index_value_variations(keyword):

                if variation not in index:
                    index[variation] = []

                index[variation].append(record)

    @classmethod
    def index_by(cls, key, value, record, game):

        cls.check_index_value(key, value)

        method = None

        if key in cls.UNIQUE_INDEXES:
            method = cls.unique_index_by

        elif key in cls.INDEXES:
            method = cls.normal_index_by

        elif key in cls.STRING_INDEXES:
            method = cls.string_index_by

        else:
            raise IndexError("Index for {} key '{}' not defined".format(
                cls.__name__,
                key,
            ))

        method(key, value, record, game)

    def index(self):

        for key in self.INDEXES + self.UNIQUE_INDEXES + self.STRING_INDEXES:
            value = self.get(key, None)

            self.index_by(key, value, self, self.game)

    @classmethod
    def check_index_value(cls, key, value):
        # if value is None or value == "":
        #     raise ValueError("Cannot index {} key '{}' with no value".format(
        #         cls.__name__,
        #         key,
        #     ))
        pass

    @classmethod
    def unique_deindex_by(cls, key, value, record, game):
        if not value:
            return

        index = cls.get_game_index(game, key)
        del index[value]

    @classmethod
    def normal_deindex_by(cls, key, value, record, game):
        if not value:
            return

        index = cls.get_game_index(game, key)
        index[value].remove(record)

    @classmethod
    def string_deindex_by(cls, key, value, record, game):
        if not value:
            return

        index = cls.get_game_index(game, key)

        values = value
        if type(values) is str:
            values = values.split()

        for keyword in values:
            for variation in cls.get_string_index_value_variations(keyword):
                index[variation].remove(record)

    @classmethod
    def deindex_by(cls, key, value, record, game):

        cls.check_index_value(key, value)

        if key in cls.UNIQUE_INDEXES:
            cls.unique_deindex_by(key, value, record, game)

        elif key in cls.INDEXES:
            cls.normal_deindex_by(key, value, record, game)

        elif key in cls.STRING_INDEXES:
            cls.string_deindex_by(key, value, record, game)

        else:
            raise IndexError("Index for {} key '{}' not defined".format(
                cls.__name__,
                key,
            ))

    def deindex(self):
        for key in self.INDEXES + self.UNIQUE_INDEXES + self.STRING_INDEXES:
            value = self.get(key, "")

            self.deindex_by(key, value, self, self.game)

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
    def filter_index_by_keywords(cls, index, keywords):

        if type(keywords) is str:
            keywords = keywords.split()

        # In order to match, it must match all keywords
        matches_by_uid = {}
        matches = []

        for keyword_index, keyword in enumerate(keywords):
            cleaned = keyword.lower()

            if cleaned in index:
                # Keep track of list to check for final union.
                results = index[cleaned]
                for result in results:
                    matches_by_uid[result.uid] = result
                matches.append({result.uid for result in results})

            # If any of these indexes do not match, failure.
            else:
                return []

        # Intersection of all the matches.
        for _ in range(1, len(keywords)):
            matches[0] = matches.pop(0) & matches[0]

        final_matches = []
        for uid in matches[0]:
            final_matches.append(matches_by_uid[uid])

        return final_matches

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

        # Keyword-searching.
        if field in cls.STRING_INDEXES:
            for record in cls.filter_index_by_keywords(index, value):
                yield record

        elif value in index:
            records = index[value]

            # Only one value possible, if available.
            if field in cls.UNIQUE_INDEXES:
                record = records
                yield record

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
            for potential in Character.query_by("name", raw_target, game=self.game):
                if self.can_see(potential):
                    target = potential

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
