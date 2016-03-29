from mud.entities.room import Room
from mud.game_entity import GameEntity
from mud.event import Event
from utils.entity import Entity


def direction_command(actor, command, *args, **kwargs):
    # FIXME add actor.can_walk() check

    current_room = actor.get_room()
    exit = current_room.get_exit(command)

    if not exit:
        actor.echo("Alas, you can't go that way.")
        return

    event_data = {
        "exit": command
    }

    exiting_event = actor.event_to_room(
        "exiting",
        event_data,
        room=current_room
    )

    if exiting_event.is_blocked():
        return

    target_room = exit.get_room()

    entering_event = actor.event_to_room(
        "entering",
        event_data,
        room=target_room
    )

    if entering_event.is_blocked():
        return

    actor.set_room(target_room)
    actor.handle_input("look")

    actor.event_to_room("exited", event_data, room=current_room)
    actor.event_to_room("entered", event_data, room=target_room)

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
     The Steam Engines & Boilers Of Waterdeep "City Of Splendors"\
 """)

    actors = Actor.query_by_room_uid(actor.room_uid)
    for other in actors:
        if not actor.can_see(other):
            continue

        output = str(other.format_room_flags_to(actor))
        output += ' '
        output += str(other.format_room_name_to(actor))

        actor.echo(output)


def bash_command(actor, *args, **kwargs):
    actor.echo("But you aren't fighting anyone!")
    actor.delay(2)


def say_command(actor, params, *args, **kwargs):
    # TODO Check nochan or nosay
    if not params:
        actor.echo("Say what?")
        return

    event_data = {
        "channel": "say",
        "message": "message",
    }

    event = actor.event_to_room("channeling", event_data)

    if event.is_blocked():
        return

    message = ' '.join(params)

    # FIXME remove this once event handling is complete
    actor.echo("{{MYou say {{x'{{m{}{{x'".format(
        message,
    ))

    actors = Actor.query_by_room_uid(actor.room_uid)
    for other in actors:
        other.echo("{{M{} says {{x'{{m{}{{x'".format(
            actor.format_name_to(other),
            message,
        ))

    actor.event_to_room("channeled", event_data)


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

    def has_effect(self, effect):
        return effect == "shock_shield"

    def is_immortal_questing(self):
        return False

    def is_good_align(self):
        return False

    def is_evil_align(self):
        return False

    def format_prompt(self):
        return "[7999/8101h 8669/12607m 1248v {}(3883) Baths(5/7am) -231] ".format(
            self.name
        )

    def format_room_flags_to(self, other):
        output = "{x["

        has_flags = False
        for color, flag, func in (
            ("{y", "V", lambda: self.has_effect("invis")),
            ("{8", "H", lambda: self.has_effect("hide")),
            ("{c", "C", lambda: self.has_effect("charm")),
            ("{b", "T", lambda: self.has_effect("pass_door")),
            ("{b", "T", lambda: self.has_effect("pass_door")),
            ("{w", "P", lambda: self.has_effect("faerie_fire")),
            ("{C", "I", lambda: self.has_effect("ice_shield")),
            ("{r", "F", lambda: self.has_effect("fire_shield")),
            ("{B", "L", lambda: self.has_effect("shock_shield")),
            ("{R", "E", lambda: self.is_evil_align()),
            ("{Y", "G", lambda: self.is_good_align()),
            ("{W", "G", lambda: self.has_effect("sanctuary")),
            ("{G", "Q", lambda: self.is_immortal_questing()),
        ):

            output += color
            if func():
                has_flags = True
                output += flag
            else:
                output += "."

        output += "{x]"

        return output

    def get_room(self):
        return Room.find_by_uid(self.room_uid)

    def format_room_name_to(self, other):
        return self.room_name

    def format_name_to(self, other):
        return self.name if other.can_see(self) else "Someone"

    def event_to_room(self, name, data=None, room=None):
        # TODO broadcast to engine
        print("TODO: Implement event broadcast for {} with data {}".format(
            name,
            repr(data)
        ))
        event = Event(name, data)
        return event

    def set_room(self, room):
        self.room_id = room.id
        self.room_uid = room.uid

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

        match = self.find_command(command)
        if not match:
            self.echo("Huh? (Command not found.)")
            return

        try:
            match["handler"](
                actor=self,
                params=params,
                command=match["keywords"].split()[0],
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

        # FIXME use config
        for direction in ["north", "south", "east", "west", "up", "down"]:
            commands.insert(0, {
                "keywords": direction,
                "handler": direction_command
            })

        word = word.lower()

        for command in commands:
            if command["keywords"].startswith(word):
                return command

        return None
