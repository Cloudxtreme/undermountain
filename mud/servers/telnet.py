"""
TELNET
"""

import gevent
import socket

from gevent import Greenlet
from gevent import monkey
from mud.entities.character import Character
from utils.ansi import Ansi

monkey.patch_all()


class TelnetConnection(Greenlet):
    NEWLINE = "\r\n"

    def __init__(self, server, conn, addr):
        super(TelnetConnection, self).__init__()
        self.playing = False
        self.server = server
        self.socket = conn
        self.address = addr
        self.username = ""
        self.input_buffer = []
        self.output_buffer = ''
        self.last_character_sent = ''
        self.state = 'login_username'
        self.game = server.get_game()
        self.delay = 0
        self.actor = None
        self.color = True
        self.last_command = ""

    def is_playing(self):
        return self.playing

    def get_actor(self):
        return self.actor

    def toggle_color(self):
        self.color = not self.color

    def has_color(self):
        return self.color

    def add_delay(self, seconds):
        self.delay += seconds

    def handle_login_username_input(self, message):
        self.username = Character.get_clean_name(message)

        if not self.username:
            self.write("Sorry, try again: ")
        else:
            ch_data = Character.get_from_file(self.username)

            if not ch_data:
                self.actor = Character(self.game, {
                    "uid": self.username,
                    "id": self.username,
                    "name": self.username,
                    "room_id": "westbridge:3001",
                })
                self.actor.set_connection(self)

                self.state = "create_confirm_username"
                self.write("""\
+------------------------[ Welcome to Waterdeep ]-------------------------+

  We are a roleplaying -encouraged- mud, meaning roleplaying is not
  required by our players but we ask that non-roleplayers abide to a few
  rules and regulations.  All names are to be roleplayish in nature and
  this policy is enforced by the staff.

    1. Do not use names such as Joe, Bob, Larry, Carl and so forth.
    2. Names of Forgotten Realms Deities are reserved for staff members.
    3. Do not use combo word names such as Blackbeard or Rockdeath, etc.

  If we find your name is not suitable for our environment, an immortal
  staff member will appear before you and offer you a rename.  Please be
  nice and civil, and we will return with the same.

+--------------[ This MUD is rated R for Mature Audiences ]---------------+

Did I get that right, {} (Y/N)? """.format(
                    self.username
                ))
                return

            self.write("Password: ")
            self.state = "login_password"

    def handle_login_password_input(self, message):
        ch_data = Character.get_from_file(self.username)
        cleaned = message.strip()
        password = Character.get_password_hash(cleaned)

        if password == ch_data["password"]:
            connection = self.game.get_actor_connection(actor_id=self.username)

            if connection is None:
                Character.add(ch_data)
                ch = Character.get_by_uid(self.username)
                self.actor = ch
                self.actor.set_connection(self)
                self.state = "motd"
                self.display_motd()

            else:
                connection.close()
                self.actor = connection.actor
                self.actor.set_connection(self)
                self.server.remove_connection(connection)
                self.state = "playing"
                self.playing = True

                self.writeln("Reconnecting..")
                self.writeln()

                self.actor.handle_input("look")
        else:
            self.writeln("Invalid password.")
            self.destroy()

    def destroy(self):
        self.playing = False
        self.flush()
        self.server.remove_connection(self)
        self.close()

    def clean_input(self, message):
        cleaned = message.lower().strip()
        return cleaned

    def handle_create_confirm_username_input(self, message):
        cleaned = self.clean_input(message)

        if cleaned.startswith("y"):
            self.write("""\
A new life has been created.

Please choose a password for {}: """.format(
                self.actor.name
            ))
            self.state = "create_password"

        elif cleaned.startswith("n"):
            self.actor = None
            self.state = "login_username"

            self.writeln()
            self.write("Ok, what IS it, then? ")
        else:
            self.write("Please type Yes or No: ")

    def handle_create_password_input(self, message):
        cleaned = message.strip()

        if not cleaned:
            self.writeln("You didn't provide a password, please try again.")
            self.write("Password: ")

        self.actor.password = Character.get_password_hash(cleaned)
        self.write("Please confirm your password: ")
        self.state = "create_password_confirm"

    def handle_create_password_confirm_input(self, message):
        cleaned = message.strip()

        if Character.get_password_hash(cleaned) != self.actor.password:
            self.writeln("Passwords don't match.")
            self.write("Retype password: ")
            self.state = "create_password"
            return

        self.writeln("""\
+---------------------------[ Pick your Race ]----------------------------+

  Welcome to the birthing process of your character.  Below you will
  find a list of available races and their basic stats.  You will gain
  an additional +2 points on a specific stat depending on your choice
  of class.  For detailed information see our website located at
  http://waterdeep.org or type HELP (Name of Race) below.

            STR INT WIS DEX CON                 STR INT WIS DEX CON
  Avian     17  19  20  16  17      HalfElf     17  18  19  18  18
  Centaur   20  17  15  13  21      HalfOrc     19  15  15  20  21
  Draconian 22  18  16  15  21      Heucuva     25  10  10  25  25
  Drow      18  22  20  23  17      Human       21  19  19  19  21
  Dwarf     20  18  22  16  21      Kenku       19  19  21  20  19
  Elf       16  20  18  21  15      Minotaur    23  16  15  16  22
  Esper     14  21  21  20  14      Pixie       14  20  20  23  14
  Giant     22  15  18  15  20      Podrikev    25  18  18  15  25
  Gnoll     20  16  15  20  19      Thri'Kreen  17  22  22  16  25
  Gnome     16  23  19  15  15      Titan       25  18  18  15  25
  Goblin    16  20  16  19  20      Satyr       23  19  10  14  21
  Halfling  15  20  16  21  18

+-------------------------------------------------------------------------+

Please choose a race, or HELP (Name of Race) for more info: \
""")
        self.state = "create_race"

    def handle_create_race_input(self, message):
        from settings.races import RACES

        cleaned = self.clean_input(message)

        for race in RACES:
            if race["id"].startswith(cleaned):
                self.actor.race_id = race["id"]
                self.write("""\
+--------------------------[ Pick your Gender ]---------------------------+

                                  Male
                                  Female
                                  Neutral

+-------------------------------------------------------------------------+

Please choose a gender for your character: """)
                self.state = "create_gender"
                return

        self.writeln("That's not a race.")
        self.write("What IS your race? ")

    def handle_create_gender_input(self, message):
        cleaned = self.clean_input(message)
        for gender_id in ["male", "female", "neutral"]:
            if gender_id.startswith(cleaned):
                self.actor.gender_id = gender_id
                break

        if self.actor.gender_id:
            self.write("""\
+--------------------------[ Pick your Class ]---------------------------+

  Waterdeep has a 101 level, 2 Tier remorting system.  After the first
  101 levels you will reroll and be able to choose a new race and class.
  2nd Tier classes are upgrades from their 1st tier counterparts.

  For more information type HELP (Name of Class) to see their help files.

                               Mage
                               Cleric
                               Thief
                               Warrior
                               Ranger
                               Druid
                               Vampire

+-------------------------------------------------------------------------+

Select a class or type HELP (Class) for details: """)
            self.state = "create_class"
        else:
            self.writeln("That's not a sex.")
            self.write("What IS your sex?")

    def handle_create_class_input(self, message):
        self.write("""\
+------------------------[ Pick your Alignment ]-------------------------+

  Your alignment will effect how much experience you get from certain
  mobiles, such as you gain less experience if you are evil, and you kill
  evil mobiles.  You gain more for killing good mobiles.  There are spells
  available that can counter this effect.

                                  Good
                                  Neutral
                                  Evil

+-------------------------------------------------------------------------+

Choose your alignment: """)
        self.actor.class_id = "warrior"
        self.state = "create_alignment"

    def handle_create_alignment_input(self, message):
        self.actor.alignment = 0
        self.write("""\
+----------------------[ Character Customization ]-----------------------+

  Your character is given a basic set of skills and or spells depending
  on your choice of class.  You can customize your character which allows
  you to choose from a wider range of skills and abilities.

+-------------------------------------------------------------------------+

Do you wish to customize? (Yes or No): """)
        self.state = "create_customize_prompt"

    def handle_create_customize_prompt_input(self, message):
        self.write("""\
+-------------------------[ Pick your Weapon ]---------------------------+

  Please pick a weapon to learn from the following choices:

  dagger
+-------------------------------------------------------------------------+


Your choice?: """)
        self.state = "create_weapon"

    def handle_create_weapon_input(self, message):
        self.display_motd()
        self.state = "motd"

        Character.add(self.actor.data)
        self.actor = Character.get_by_uid(self.actor.uid)
        self.actor.set_connection(self)

        # First save!
        self.actor.save()

    def handle_motd_input(self, message):
        self.state = "playing"
        self.playing = True
        self.actor.handle_input("look")

    def handle_playing_input(self, message):
        # FIXME improve this or use constant?
        if message.strip() == "":
            self.write(" ")
            return

        if message.startswith("!"):
            self.handle_playing_input(self.last_command)
            return

        self.last_command = message
        self.actor.handle_input(message)

    def handle_input(self, message):
        message = message.strip()

        method_name = 'handle_{}_input'.format(self.state)
        if not hasattr(self, method_name):
            raise Exception("Invalid TelnetConnection state '{}'".format(
                self.state
            ))

        method = getattr(self, method_name)
        try:
            method(message)
        except Exception, e:
            self.game.handle_exception(e)

    def display_motd(self):
        self.writeln("MOTD")
        self.writeln()
        self.writeln("Press any key to continue")

    def write_from_template(self, template):
        path = "templates/telnet/" + template
        try:
            with open(path, "r") as template_file:
                contents = template_file.read()
                self.write(contents.strip("\r\n"))
        except IOError:
            self.writeln("Unable to load template '{}'".format(path))

    def flush(self):
        if self.output_buffer:

            # Prefix a newline if we didn't send one last time.
            if self.last_character_sent != self.NEWLINE[-1]:
                self.output_buffer = self.NEWLINE + self.output_buffer

            if self.actor:
                self.writeln()
                if self.playing:
                    if self.actor.is_fighting():
                        self.writeln(self.actor.format_combat_prompt())
                    self.write(self.actor.format_prompt())

            self.last_character_sent = self.output_buffer[-1]
            self.socket.sendall(self.output_buffer)
            self.output_buffer = ''

    def input_loop(self):
        while self.connected:

            # Handle any imposed delay on user input by the game.
            delay = self.delay
            self.delay = 0
            if delay:
                gevent.sleep(delay)

            # FIXME make this cleaner?
            # Allow players to clear their input buffer.
            if "clear" in self.input_buffer:
                self.input_buffer = []
                self.writeln("Input buffer cleared.")

            # Pop off a command and execute it.
            if self.input_buffer:
                next_input = self.input_buffer.pop(0)
                self.handle_input(next_input)
                gevent.sleep(0.5)
            else:
                gevent.sleep(0.05)

    def _run(self):
        # self.write_from_template("login")
        self.writeln("Undermountain")
        self.writeln()
        self.write("Username: ")

        gevent.spawn(self.input_loop)

        self.connected = True
        while self.connected:
            try:
                raw_message = self.socket.recv(4096)
            except Exception:
                raw_message = None
            if raw_message:
                lines = raw_message.strip("\r\n").split("\n")
                self.input_buffer += lines
            else:
                self.connected = False

    def read(self):
        if self.lines:
            return self.lines.pop()
        return None

    def write(self, message=""):
        if self.color:
            message = Ansi.colorize(message)

        self.output_buffer += message

    def writeln(self, message=""):
        self.write(message + self.NEWLINE)

    def close(self):
        self.connected = False
        try:
            self.socket.shutdown(socket.SHUT_WR)
            self.socket.close()
        except Exception:
            pass


class TelnetServer(Greenlet):
    def __init__(self, game):
        super(TelnetServer, self).__init__()
        self.game = game
        self.connections = []
        self.running = False

    def get_game(self):
        return self.game

    def output_loop(self):
        while self.running:
            for connection in self.connections:
                connection.flush()
            gevent.sleep(0.05)

    def remove_connection(self, connection):
        self.connections.remove(connection)
        self.game.remove_connection(connection)

    def add_connection(self, connection):
        self.connections.append(connection)
        self.game.add_connection(connection)

    def _run(self):
        self.running = True

        gevent.spawn(self.output_loop)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        host = '0.0.0.0'
        port = 3200
        print("Listening on {}:{}".format(host, port))

        sock.bind((host, port))
        sock.listen(1)

        while self.running:
            conn, addr = sock.accept()
            connection = TelnetConnection(self, conn, addr)
            self.add_connection(connection)
            connection.start()

        sock.shutdown(socket.SHUT_WR)
        sock.close()
