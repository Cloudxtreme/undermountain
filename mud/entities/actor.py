from mud.room_entity import RoomEntity
from mud.entities.object import Object
from mud.entities.combat import Combat
from utils.entity import Entity

def nocommand_command(actor, params, command, *args, **kwargs):

    # Nothing provided.
    if not len(params):
        actor.echo("Limit a player from being able to use a command.")
        actor.echo("Usage: {} <name> <command>".format(command))
        return

    # Show nocommands for a player.
    elif len(params) == 1:
        actor.echo("List nocommands.")
        return

    actor.echo("Implement nocommand.")


def password_command(actor, params, *args, **kwargs):
    from mud.entities.character import Character

    if len(params) < 2:
        actor.echo("Usage: password <old> <new>")
        return

    old = Character.get_password_hash(params[0])
    new = Character.get_password_hash(params[1])

    if actor.password != old:
        actor.echo("Invalid old password.")
        return

    actor.password = new
    actor.save()
    actor.echo("Password updated.")


def quit_command(actor, *args, **kwargs):
    actor.act_around("[actor.name] slowly fades into existence.")
    actor.echo("""\
{RYou feel a hand grab you, you begin to fly upwards!
{BYou pass through the clouds and out of the world!
{GYou have rejoined Reality!

{WFor {RNews{W, {CRoleplaying{W and {MInfo, {WVisit our website!
{Ch{cttp://{Cw{cww{x.{Cw{caterdeep{x.{Co{crg{x""")

    # TODO Check actor can quit here.

    connection = actor.get_connection()
    connection.destroy()


def prompt_command(actor, params, *args, **kwargs):
    if not params:
        actor.echo("Prompt set to default.")
        actor.clear_prompt()
        return

    prompt = " ".join(params)
    actor.prompt = prompt
    actor.echo("Prompt set to: {}{{x".format(prompt))

def commands_command(actor, *args, **kwargs):
    actor.echo("Available commands:")
    for command in actor.query_command_handlers():
        actor.echo(command["keywords"])

def title_command(actor, params, *args, **kwargs):
    # FIXME add truncation

    title = ""
    if params:
        title = " ".join(params)

    actor.title = title

    if not params:
        actor.echo("Your title has been cleared.")
    else:
        actor.echo("Your title has been set to: {}{{x".format(title))

def string_command(actor, params, *args, **kwargs):
    remainder = list(params)

    CHAR_STRINGS = ["who", "who_class", "who_race", "who_clan", "who_gender",
                    "who_level", "who_flags", "bracket", "title"]

    def show_string_help(actor):
        actor.echo("string char <name> <field> [value]")
        actor.echo("Fields: " + (" ".join(CHAR_STRINGS)))

    if not remainder:
        show_string_help(actor)
        return

    stringtype = remainder.pop(0)
    if stringtype == "char":

        if not remainder:
            actor.echo("Character name not provided.")
            show_string_help(actor)
            return

        name = remainder.pop(0)
        target = actor.game.find_character(func=lambda other: other.name_like(name))

        if not target:
            actor.echo("Character '{}' not found.".format(name))
            return

        if not remainder:
            actor.echo("Field not provided.")
            show_string_help(actor)
            return

        field = remainder.pop(0)
        if field in CHAR_STRINGS:
            value = " ".join(remainder) if remainder else ""
            target[field] = value

            actor.echo("String '{}{{x' set for {}{{x: {}{{x".format(
                target.name,
                field,
                value
            ))
        else:
            actor.echo("Field '{}' not found.".format(field))
            show_string_help(actor)

    else:
        show_string_help(actor)


def tell_command(actor, params, *args, **kwargs):
    target = params[0] if len(params) > 0 else None
    message = ' '.join(params[1:]) if len(params) > 1 else None

    actor.tell(target, message)

def kill_command(actor, params, *args, **kwargs):
    if not params:
        actor.echo("Kill who?")
        return

    room = actor.get_room()
    # TODO improve this logic with something like actor.find_visible_target_by_name
    # FIXME improve this to use query logic
    target = room.query_actors(cmp=lambda other:
        other != actor and
        other.name_like(params) and
        actor.can_see(other)
    )

    if not target:
        actor.echo("You can't kill what you can't find.")
        return

    if actor.can_attack(target):
        actor.echo("You can't attack that target.")
        return

    actor.attack(target)


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

def get_who_level_value(actor):
    if actor.has_role("admin"):
        return 110

    if actor.has_role("builder"):
        return 109

    if actor.has_role("immortal"):
        return 102

    return actor.get_level()

def who_command(actor, game, *args, **kwargs):
    from utils.ansi import Ansi

    actor.echo("""\
{G                   The Visible Mortals and Immortals of Waterdeep
{g-----------------------------------------------------------------------------\
    """)

    total_count = 0
    visible_count = 0

    chars = list(game.query_characters())
    for other in sorted(chars, key=get_who_level_value, reverse=True):
        total_count += 1

        if not actor.can_see(other):
            continue

        visible_count += 1

        output = "{x"

        if other.who_level:
            output += Ansi.pad_right(other.who_level, 4)
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

        if other.who:
            output += Ansi.pad_right(other.who, 18) + "{x"
        else:
            if other.who_gender:
                output += Ansi.pad_right(other.who_gender, 2)
            else:
                output += other.format_who_gender() + " "
            output += "{x"

            if other.who_race:
                output += Ansi.pad_right(other.who_race, 6)
            else:
                output += Ansi.pad_right(other.format_who_race(), 6)
            output += "{x"

            if other.who_class:
                output += Ansi.pad_right(other.who_class, 4)
            else:
                output += Ansi.pad_right(other.format_who_class(), 4)
            output += "{x"

            if other.who_clan:
                output += Ansi.pad_right(other.who_clan, 6)
            else:
                output += Ansi.pad_right(other.format_who_clan(), 6)
            output += "{x"

        if other.who_flags:
            flags_length = 10 if other.has_role("immortal") else 8
            output += "[" + Ansi.pad_right(other.who_flags, flags_length, ".") + "{x]"

        elif other.has_role("immortal"):
            output += "[..........]"
        else:
            output += "[........]"

        output += "{x "

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
    actor.echo("Saving..")
    actor.save()
    actor.echo("Saved.")


def channel_command(actor, command, params, *args, **kwargs):
    from mud.exceptions import CommandNotFound
    from settings.channels import CHANNELS
    channel = CHANNELS[command]

    if not params:
        actor.echo("Channel toggling not yet implemented.")
        return

    message = " ".join(params)

    # Check Player can access channel.
    access_func = channel.get("access")
    if access_func is not None and not access_func(actor):
        raise CommandNotFound()

    for target in actor.game.query_characters():

        filter_func = channel.get("filter")
        if filter_func is not None and not filter_func(actor, target):
            continue

        replaces = {
            "[actor.name]":
                actor.name if channel.get("name_always", False) else
                actor.format_name_to(target),
            "[message]": message
        }

        template = channel[
            "send_template" if target == actor else
            "receive_template"
        ]

        for field, value in replaces.iteritems():
            template = template.replace(field, value)

        target.echo(template)


def walk_command(actor, command, *args, **kwargs):
    from utils.time import Time

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

    actor.act_around("[actor.name] leaves to the {}".format(command))

    exiting_event = actor.event_to_room(
        "exiting",
        event_data,
        room=current_room,
        blockable=True
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

    actor.act_around("[actor.name] enters the room.")

    actor.event_to_room("exited", event_data, room=current_room)
    actor.event_to_room("entered", event_data, room=target_room)


def affects_command(actor, *args, **kwargs):
    effects = actor.get_effects()

    if not effects:
        actor.echo("You are not affected by any spells.")
        return

    actor.echo("You are affected by the following spells:")
    for effect in effects:
        line = effect["label"] if effect.get("label") else effect["id"]
        line += " "
        line += "for {} seconds".format(effect["seconds"])
        actor.echo(line)


def bash_command(actor, *args, **kwargs):
    actor.echo("But you aren't fighting anyone!")
    actor.delay(2)


def sayooc_command(*args, **kwargs):
    kwargs["ooc"] = True
    return say_command(*args, **kwargs)

def say_command(actor, params, ooc=False, *args, **kwargs):

    if actor.has_flag("nochan") or actor.has_flag("nosay"):
        actor.echo("You cannot say anything.")
        return

    # TODO Check nochan or nosay
    if not params:
        actor.echo("Say what?")
        return

    message = ' '.join(params)

    actor.say(message, ooc=ooc)


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

        if type(self.effects) is not list:
            self.effects = [
                {"id": "poison", "seconds": 5, "expire_message": "Your poison fades."},
                {"id": "poison", "seconds": 10, "expire_message": "Your second poison fades."},
            ]

        if type(self.nochans) is not list:
            self.nochans = []

    def clear_prompt(self):
        self.prompt = None

    def has_flag(self, flag):
        # FIXME to implement
        return False

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

    def get_health_percent(self):
        """
        Get this actor's health percentage, as a float representing the
        percentage of health remaining.  ex: 1.0 = 100%, 0.53 = 53%
        """
        return 1.0

    def get_health_color(self):
        percent = self.get_health_percent()
        if percent >= (2/3):
            return "G"

        if percent >= (1/3):
            return "Y"

        return "R"

    def format_combat_prompt(self):
        target = self.get_combat_target()
        if target is None:
            return ""

        return "{{R{} {{Ris in excellent condition. {{x[{{{}{}%{{x]".format(
            target.format_name_for(self),
            target.get_health_color(),
            int(target.get_health_percent() * 100)
        )
        get_combat_target

    def format_prompt(self):
        prompt = self.prompt

        if not prompt:
            prompt = "{R100{8/{R100{Chp {G100{8/{G100{Cmana {Y1000{Cxp {8%N{x>"

        prompt = prompt.replace("%N", self.name)

        return prompt + " "

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
        return self.get("name", "Someone") if other.can_see(self) else "Someone"

    def delay(self, seconds):
        """
        Delay a player's next command interpretation in seconds.
        """
        connection = self.get_connection()
        if connection:
            connection.add_delay(seconds)

    def get_connection(self):
        return self.connection

    def set_connection(self, connection):
        super(Entity, self).__setattr__('connection', connection)

    def echo(self, message=""):
        message = str(message)

        connection = self.get_connection()
        if connection:
            connection.writeln(message)

    def handle_input(self, message):
        from mud.exceptions import CommandNotFound

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
                game=self.game,
                params=params,
                command=match["keywords"].split()[0],
            )

        except CommandNotFound:
            self.echo("Huh? (Command not found.)")

        except Exception, e:
            self.echo("Huh?! (Exception in handler.)")
            self.game.handle_exception(e)

    def find_command_handler(self, word):
        command = self.find_command(word)

        if command:
            return command["handler"]

        return None

    def name_like(self, params):
        if type(params) is None:
            return False

        # TODO improve this to use mob keywords
        if type(params) is not tuple:
            params = tuple(params)

        for param in params:
            matches = False
            for keyword in self.keywords:
                if keyword.startswith(param):
                    matches = True
                    break

            if not matches:
                return False

        return True

    def can_attack(self, target):
        return False

    def query_command_handlers(self):
        from settings.directions import DIRECTIONS
        from settings.channels import CHANNELS

        commands = [
            {
                "keywords": "password",
                "handler": password_command,
            },
            {
                "keywords": "quit",
                "handler": quit_command,
            },
            {
                "keywords": "commands",
                "handler": commands_command,
            },
            {
                "keywords": "affects",
                "handler": affects_command
            },
            {
                "keywords": "nocommand",
                "roles": ["admin"],
                "handler": nocommand_command
            },
            {
                "keywords": "effects",
                "handler": affects_command
            },
            {
                "keywords": "title",
                "handler": title_command
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
                "keywords": "sayooc",
                "handler": sayooc_command
            },
            {
                "keywords": "save",
                "handler": save_command
            },
            {
                "keywords": "tell",
                "handler": tell_command
            },
            {
                "keywords": "who",
                "handler": who_command
            },
            {
                "keywords": "prompt",
                "handler": prompt_command
            },
            # {
            #     "keywords": "reload",
            #     "handler": reload_command
            # },
            {
                "keywords": "kill",
                "handler": kill_command
            },
            {
                "keywords": "string",
                "handler": string_command
            },
        ]

        from mud.commands.sockets import sockets_command
        commands.append({"keywords": "sockets", "handler": sockets_command, "role": "admin"})

        from mud.commands.map import map_command
        commands.append({"keywords": "map", "handler": map_command})

        from mud.commands.look import look_command
        commands.append({"keywords": "look", "handler": look_command})

        # FIXME use config
        for direction in DIRECTIONS.keys():
            commands.insert(0, {
                "keywords": direction,
                "handler": walk_command
            })

        # FIXME use config
        for channel in CHANNELS.keys():
            commands.insert(0, {
                "keywords": channel,
                "handler": channel_command
            })

        return commands

    def find_command(self, word):
        commands = self.query_command_handlers()

        word = word.lower()

        for command in commands:
            if command["keywords"].startswith(word):
                roles = command.get("roles", [])

                role = command.get("role", None)
                if role:
                    roles.append(role)

                if not roles:
                    return command
                else:
                    for role in roles:
                        if self.has_role(role):
                            return command

        return None

    def attack(self, other):
        room = self.get_room()
        battle = Combat.get_by_actor(self)

        if battle:
            self.echo("You are already fighting someone.")
            return

        Combat.initiate_combat(self, other)

    def damage(self, target, amount, skill=None, label=None, type=None, element=None, counterable=False, lethal=True, silent=False):
        # Your creeping doom COMPLETELY TRASHES a dark elven figure! -=813=-
        self.echo("Your {} {} {}{} -={}=-".format(
            label if label is not None else "attack",
            "COMPLETELY TRASHES",
            target.format_name_to(self),
            "!" if amount > 100 else ".",
            amount
        ))
        target.echo("{}'s {} {} you{} -={}=-".format(
            self.format_name_to(target),
            label if label is not None else "attack",
            "COMPLETELY TRASHES",
            "!" if amount > 100 else ".",
            amount
        ))

    def get_combat_target(self):
        battle = Combat.get_by_actor(self)
        if battle is None:
            return None

        for actor in battle.actors:
            if actor == self:
                continue
            return actor
        return None

    def is_fighting(self):
        battle = Combat.get_by_actor(self, self.game)
        return battle is not None

    def tell(self, raw_target, message):
        """
        Tell another player a message.

        tell <name> <message>
        """
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

    def get_effects(self):
        return self.effects

    @classmethod
    def find(cls, game, func=None):
        for actor in cls.query(game=game):
            if func and func(actor):
                return actor
        return None

    def tick(self):
        self.tick_effects()

    def get_level(self):
        return self.get("level", 1)

    def expire_effect(self, effect):
        self.echo(effect["expire_message"])
        self.effects.remove(effect)

    def has_clan(self):
        return self.get("clan_id", None) is not None

    def is_maximum_level(self):
        from mud.settings.game import MAX_LEVEL
        return self.level == MAX_LEVEL

    def save(self):
        """
        Save Actor.
        This is a stub, but others can save to files.
        """
        pass

    def tick_effects(self):
        for effect in self.effects[:]:
            effect["seconds"] -= 1
            if effect["seconds"] <= 0:
                self.expire_effect(effect)
