from mud.game_entity import GameEntity


class Actor(GameEntity):
    """
    ACTOR
    A creature, monster, person, etc. that is 'alive' in the World.
    """
    COLLECTION_NAME = 'actors'

    def handle_input(self, message):
        connection = self.game.get_actor_connection(self)
        connection.writeln("HANDLING INPUT> " + message)
