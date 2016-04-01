from mud.room_entity import RoomEntity
from mud.entities.object import Object
from utils.entity import Entity


def who_command(actor, *args, **kwargs):
    actor.echo("""\
{G                   The Visible Mortals and Immortals of Waterdeep
{g-----------------------------------------------------------------------------\
    """)
# IMP M Coder God Coder [..LPM....B] Kelemvor Lord of Death [Software Development]
# IMP M Coder God Coder [..LPM....B] Kelemvor Lord of Death [Software Development]
# CRE F Human Ran       [W.PNMR...B] Mielikki May be here, but may not [Our Lady of the Forests]
# SUP M Dwarf Gla       [W..N......] Dumathoin Keeper of Secrets Under the Mountain
# DEI M Giant God UnDrk [...NMR....] Torog is digging, always digging. [Roleplay Immortal]
# DEI M Dragn God       [...NMR....] Bahamut. [The Platinum Dragon]
# GOD M Thken Cle Quest [...P......] Jergal The Lord of the End of Everything [Scrivener of Doom]
# IMM F Carnl Joy       [...N.R....] Sharess the Naughty Dancer.
# HRO M Human Mer BlkCh   [.P......] Frast Daftest of punks [CDXX]
# HRO M Heucv Gla RdHrt   [.P......] Morholt Silent Destruction
# HRO F H.Elf Str Vectr   [.P.R....] Hannah. [Imperial Princess]
# HRO M Human Lic Hoard   [LP......] Oreza, Merchant Of Death    [vXo]
# HRO M Drow  Prs Vectr   [.N.R....] Odia V.2002 NPK base for the masses.  nVo [Assembly of Wealth] [C|ST]
# HRO M Dwarf Mnk         [.N......] Azzus is kung fu fighting
# HRO N Human Mer BlkCh   [.P.R....] Skyla The Dark Rogue [DC]
# HRO M Shadw Thi BlkCh   [.PMR....] Relic Revenu [Thief] [L|ST]
# HRO M Podkv Gla KoB     [.N......] Alejandros De La Vega (Bandolero with a Bandolier)
# HRO M Heucv Prs RdHrt   [.P......] Null Doomguide
# 90 M Hflng Mnk OtLw    [.N......] Christian the Master of Summer
# 79 M H.Elf Str         [.N......] Galkar SilverLeaf
# 78 M Mntur Prs         [.N......] Bazza Horn of salvation
# 77 M Hflng Wiz KoB     [.N......] Calcifer the Master Wizard
# 54 F Esper Mer KoB     [.N......] Briar the Mistress of Hearing
# 44 M Kenku Str         [.N......] Collonwy the Manhunter

    actor.echo()
    actor.echo("{GPlayers found{g: {x23   {GTotal online{g: {W23   {GMost on today{g: {x23")

def save_command(actor, *args, **kwargs):
    actor.echo("Saving happens automatically.  This command does nothing.")


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
        if not self.prompt:
            return "{{R100{{8/{{R100{{Chp {{G100{{8/{{G100{{Cmana {{Y1000{{Cxp {{8{}{{x> ".format(
                self.name
            )

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
        ]

        # FIXME use config
        for direction in DIRECTIONS.keys():
            commands.insert(0, {
                "keywords": direction,
                "handler": direction_command
            })

        word = word.lower()

        for command in commands:
            if command["keywords"].startswith(word):
                return command

        return None
