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
        self.input_buffer = []
        self.output_buffer = ''
        self.last_character_sent = ''
        self.state = 'login_username'
        self.game = server.get_game()
        self.delay = 0
        self.actor = None
        self.color = True
        self.last_command = ""

    def toggle_color(self):
        self.color = not self.color

    def has_color(self):
        return self.color

    def add_delay(self, seconds):
        self.delay += seconds

    def handle_login_username_input(self, message):
        name = Character.get_clean_name(message)
        if not name:
            self.write("Sorry, try again: ")
        else:
            ch = Character.get_from_file(name)
            if not ch:
                self.writeln("New character path")
            else:
                self.actor = Character(self.game, ch)
                self.actor.set_connection(self)
                self.state = "motd"
                self.display_motd()

    def handle_motd_input(self, message):
        self.state = "playing"
        self.playing = True
        self.actor.handle_input("look")

    def handle_playing_input(self, message):
        # FIXME improve this or use constant?
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
                self.output_buffer += self.NEWLINE
                if self.playing:
                    self.output_buffer += self.actor.format_prompt()

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
            raw_message = self.socket.recv(4096)
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
        sock.bind(('0.0.0.0', 3200))
        sock.listen(1)

        while self.running:
            conn, addr = sock.accept()
            connection = TelnetConnection(self, conn, addr)
            self.add_connection(connection)
            connection.start()

        sock.shutdown(socket.SHUT_WR)
        sock.close()
