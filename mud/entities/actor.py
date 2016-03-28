from mud.entities.room import Room
from mud.game_entity import GameEntity
from utils.entity import Entity


def look_command(actor, *args, **kwargs):
    actor.echo("""
The Center Of Waterdeep [NOLOOT] (Limbo) (building) [Room 69]
  You stand in the center of the world, the heart of the world.
Before you stands a large cavern, not filled with lava, but with large
steam engines.  The boilers stand 20 stories tall, and little umpa
lumpas stand here, black as night shoveling coal into the boilers.  To
the north, a little balcony overlooking the crank shaft of the world.
Outside the balcony, you see a large iron shaft, going up and down.
Piston Arms jult out of the sides of the wall and turn the shaft,
slowly.  You have come to the center of the world, and now you know
what runs it.

[Exits: east west up down]   [Doors: none]   [Secret: none]
     The Steam Engines & Boilers Of Waterdeep "City Of Splendors"
    """)

    actors = Actor.query_by_room_uid(actor.room_uid)
    for other in actors:
        if not actor.can_see(other):
            continue

        output = str(other.format_room_flags_for(actor))
        output += ' '
        output += str(other.format_room_name_for(actor))

        actor.echo(output)


def bash_command(actor, *args, **kwargs):
    actor.echo("But you aren't fighting anyone!")
    actor.delay(2)


def say_command(actor, params, *args, **kwargs):
    # TODO Check nochan or nosay
    if not params:
        actor.echo("Say what?")
        return

    message = ' '.join(params)

    # FIXME remove this once event handling is complete
    actor.echo("{{MYou say {{x'{{m{}{{x'".format(
        message
    ))

    actor.event_to_room("channel", {
        "channel": "say",
        "message": "message",
    })


class Actor(GameEntity):
    """
    ACTOR
    A creature, monster, person, etc. that is 'alive' in the World.
    """
    COLLECTION_NAME = 'actors'

    def __init__(self, *args, **kwargs):
        super(Actor, self).__init__(*args, **kwargs)
        super(Entity, self).__setattr__("connection", None)

    @classmethod
    def query_by_room_uid(cls, uid, game=None):
        if not game:
            game = cls.get_game()

        return [
            cls(game, actor)
            for actor in cls.query()
            if actor.get("room_uid", None) == uid
        ]

    def can_see(self, other):
        # FIXME check for flags
        return True

    def format_room_flags_for(self, other):
        return "[........]"

    def get_room(self):
        return Room.find_by_uid(self.room_uid)

    def format_room_name_for(self, other):
        return self.room_name

    def event_to_room(self, name, data=None):
        print("EVENT_TO_ROOM NOOP FOR " + str(self))

    def delay(self, seconds):
        """
        Delay a player's next command interpretation in seconds.
        """
        if self.connection:
            self.connection.add_delay(seconds)

    def set_connection(self, connection):
        super(Entity, self).__setattr__("connection", connection)

    def echo(self, message):
        message = str(message)

        if self.connection:
            self.connection.writeln(message)

    def handle_input(self, message):
        self.echo("HANDLING INPUT> " + message)

        parts = message.split(' ')

        if not parts:
            # TODO Some kind of noop in telnet client?
            return

        command = parts.pop(0)
        params = tuple(parts)

        handler = self.find_command_handler(command)
        if not handler:
            self.echo("Huh? (Command not found.)")
            return

        try:
            handler(
                actor=self,
                params=params,
                command=command,
            )
        except Exception, e:
            self.echo("Huh?! (Exception in handler.)")
            self.game.handle_exception(e)

    def find_command_handler(self, word):
        command = self.find_command(word)

        if command:
            return command["handler"]

        return None

    def find_command(self, word):
        commands = [
            {
                "keywords": "look",
                "handler": look_command
            },
            {
                "keywords": "bash",
                "handler": bash_command
            },
            {
                "keywords": "say",
                "handler": say_command
            },
        ]

        word = word.lower()

        for command in commands:
            if command["keywords"].startswith(word):
                return command

        return None
