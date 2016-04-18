from mud.room_entity import RoomEntity
from mud.entities.object import Object
from utils.entity import Entity


def reload_command(actor, *args, **kwargs):
    import sys
    to_restart = ["mud", "utils"]
    for module in list(sys.modules):
        found = False

        # Exact match.
        if module in to_restart:
            found = True

        # Prefix match.
        else:
            for prefix in to_restart:
                if module.startswith(prefix + "."):
                    found = True
                    continue

        if found:
            del(sys.modules[module])

	# del(sys.modules[m])
    actor.echo("Reloaded modules.")

def who_command(actor, *args, **kwargs):
    from utils.ansi import Ansi

    actor.echo("""\
{G                   The Visible Mortals and Immortals of Waterdeep
{g-----------------------------------------------------------------------------\
    """)

    game = actor.get_game()

    total_count = 0
    visible_count = 0

    for other in game.get_characters():
        total_count += 1

        if not actor.can_see(other):
            continue

        visible_count += 1

        output = ""

        if other.level_restring:
            output += Ansi.pad_left(other.level_restring, 4)
        elif other.has_role("admin"):
            output += "{RIMP{x "
        elif other.has_role("builder"):
            output += "{GCRE{x "
        elif other.has_role("immortal"):
            output += "{GIMM{x "
        elif other.is_hero():
            output += "{BHRO{x "
        else:
            output += Ansi.pad_left("{x" + str(other.level) + "{x", 3) + " "

        if other.who_restring:
            output += Ansi.pad_right(other.who_restring, 22)
        else:
            if other.who_gender_restring:
                output += Ansi.pad_right(other.who_gender_restring, 2)
            else:
                output += other.format_who_gender() + " "

            if other.who_race_restring:
                output += Ansi.pad_right(other.who_race_restring, 6)
            else:
                output += Ansi.pad_right(other.format_who_race(), 6)

            if other.who_class_restring:
                output += Ansi.pad_right(other.who_class_restring, 4)
            else:
                output += Ansi.pad_right(other.format_who_class(), 4)

            if other.who_clan_restring:
                output += Ansi.pad_right(other.who_clan_restring, 6)
            else:
                output += Ansi.pad_right(other.format_who_clan(), 6)

        if other.who_flags_restring:
            Ansi.pad_left(other.who_flags_restring, 11)
        if other.has_role("immortal"):
            output += "[..........]"
        else:
            output += "[........]"

        output += " "

        output += other.name

        if other.title:
            output += " " + other.title

        if other.bracket:
            output += " {x[" + other.bracket + "{x]"

        faction = other.get_faction()
        if faction:
            output += " " + faction.format_who_display()

        actor.echo(output)

    highest_count = total_count

    actor.echo()
    actor.echo("{{GPlayers found{{g: {{x{}   {{GTotal online{{g: {{W{}   {{GMost on today{{g: {{x{}".format(
        visible_count,
        total_count,
        highest_count,
    ))

def save_command(actor, *args, **kwargs):
    actor.echo("Saving happens automatically.  This command does nothing.")


def walk_command(actor, command, *args, **kwargs):
    # FIXME add actor.can_walk() check

    current_room = actor.get_room()
    exit = current_room.get_exit(command)

    if not exit:
        actor.echo("Alas, you can't go that way.")
        return

    if exit.has_flag("door"):
        if exit.has_flag("closed"):
            if not actor.has_effect("pass_door"):
                actor.echo("The door is closed.")
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
    from mud.entities.character import Character
    from settings.directions import DIRECTIONS

    room = actor.get_room()

    title_line = "{}{{x {} ({}) ({}) [Room {}] [ID {}]".format(
        "{B" + room.name + "{x",
        "{R[{WNOLOOT{R]{x",
        room.area_id,
        "{Wbuilding{x",
        room.id,
        room.uid,
    )
    actor.echo(title_line)

    for index, line in enumerate(room.description):

        if index == 0:
            line = "  " + line

        actor.echo(line)

    actor.echo()

    exits = []
    doors = []
    secrets = []

    def format_exits(exits):
        if not exits:
            return "none"
        return " ".join([exit["colored_name"] for exit in exits])

    for exit_id, exit in DIRECTIONS.iteritems():
        room_exit = room.get_exit(exit_id)

        if not room_exit:
            continue

        if room_exit.has_flag("door") and room_exit.has_flag("closed"):
            if room_exit.has_flag("secret"):
                secrets.append(exit)
            else:
                doors.append(exit)
        else:
            exits.append(exit)

    exit_options = [
        ("Exits", exits),
        ("Doors", doors),
    ]
    # FIXME Add immortality check.
    if True:
        exit_options.append(("Secret", secrets))

    exit_line_parts = []
    for label, options in exit_options:
        exit_line_parts.append("{{x[{{G{}{{g:{{x {}{{x]".format(
            label,
            format_exits(options)
        ))

    actor.echo('   '.join(exit_line_parts))

    objects = Object.query_by_room_uid(actor.room_uid)
    actors = Actor.query_by_room_uid(actor.room_uid)
    characters = Character.query_by_room_uid(actor.room_uid)

    for other in objects + characters + actors:
        if not actor.can_see(other) or other == actor:
            continue

        print(other)
        output = str(other.format_room_flags_to(actor))

        # Only add space if there's a set of flags.
        if output:
            output += ' '

        if type(other) is Object:
            output = '     ' + output

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


class Actor(RoomEntity):
    """
    ACTOR
    A creature, monster, person, etc. that is 'alive' in the World.
    """
    COLLECTION_NAME = 'actors'

    def __init__(self, *args, **kwargs):
        super(Actor, self).__init__(*args, **kwargs)
        super(Entity, self).__setattr__("connection", None)

        if not self.level:
            self.level = 1

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

    def has_role(self, role):
        return role in self.get("roles", [])

    def is_immortal(self):
        return this.get("immortal", False)

    def is_hero(self):
        return self.level == 101

    def format_prompt(self):
        if not self.prompt:
            return "{{R100{{8/{{R100{{Chp {{G100{{8/{{G100{{Cmana {{Y1000{{Cxp {{8{}{{x> ".format(
                self.name
            )

        return "[7999/8101h 8669/12607m 1248v {}(3883) Baths(5/7am) -231] ".format(
            self.name
        )

    def format_who_race(self):
        return "{CH{ceucv{x"

    def get_faction(self):
        return None

    def format_who_class(self):
        return "{BG{bla{x"

    def format_who_clan(self):
        return ""

    def format_who_gender(self):
        if self.gender == "male":
            return "{BM{x"
        elif self.gender == "female":
            return "{MM{x"
        else:
            return "{8N{x"

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

        return output if has_flags else ""

    def format_name_to(self, other):
        return self.name if other.can_see(self) else "Someone"

    def delay(self, seconds):
        """
        Delay a player's next command interpretation in seconds.
        """
        if self.connection:
            self.connection.add_delay(seconds)

    def set_connection(self, connection):
        super(Entity, self).__setattr__("connection", connection)

    def echo(self, message=""):
        message = str(message)

        if self.connection:
            self.connection.writeln(message)

    def handle_input(self, message):
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
        from settings.directions import DIRECTIONS
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
            {
                "keywords": "save",
                "handler": save_command
            },
            {
                "keywords": "who",
                "handler": who_command
            },
            {
                "keywords": "reload",
                "handler": reload_command
            },
        ]

        # FIXME use config
        for direction in DIRECTIONS.keys():
            commands.insert(0, {
                "keywords": direction,
                "handler": walk_command
            })

        word = word.lower()

        for command in commands:
            if command["keywords"].startswith(word):
                return command

        return None
