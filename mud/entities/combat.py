from mud.game_entity import GameEntity


class Combat(GameEntity):
    """
    COMBAT
    A battle that is currently in progress.
    """
    COLLECTION_NAME = 'combats'

    @classmethod
    def get_by_actor(cls, actor, game=None):
        if game is None:
            game = cls.get_game()

        for combat in cls.query():
            for actor_uid in combat.actors:
                if actor_uid == actor.uid:
                    return cls.wrap(combat)

        return None


    @classmethod
    def initiate_combat(cls, actor, other, game=None):
        if game is None:
            game = cls.get_game()

        data = {
            "actors": [
                actor,
                other,
            ],
            "targets": {}
        }

        # TODO make proper combat order/targetting
        # data["targets"][actor.uid] = []

        cls.add(data)

    @classmethod
    def cancel_combat(cls, actor):
        """
        Get an Actor out of a battle.
        """
        pass

    def tick(self):
        """
        For each Actor in this battle, perform a normal round.
        """
        for actor in self.actors:
            for other in self.actors:
                if actor == other:
                    continue

                for x in range(0, 10):
                    actor.damage(
                        type="pierce",
                        target=other,
                        element="fire",
                        counterable=True,
                        amount=100,
                    )
