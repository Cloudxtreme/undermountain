"""
TELNET
"""
from gevent import Greenlet
from gevent import monkey
from mud.entities.character import Character

import gevent
import socket

monkey.patch_all()


class TelnetConnection(Greenlet):
    def __init__(self, server, conn, addr):
        super(TelnetConnection, self).__init__()
        self.playing = False
        self.server = server
        self.socket = conn
        self.address = addr
        self.input_buffer = []
        self.output_buffer = ''
        self.state = 'login_username'
        self.game = server.get_game()
        self.actor = None

    def handle_input(self, message):
        message = message.strip()

        if self.state == "login_username":
            name = Character.get_clean_name(message)
            if not name:
                self.write("Sorry, try again: ")
            else:
                ch = Character.get_from_file(name)
                if not ch:
                    self.writeln("New character path")
                else:
                    self.actor = Character(self.game, ch)
                    self.state = "motd"
                    self.display_motd()

        elif self.state == "motd":
            self.state = "playing"
            self.actor.handle_input("look")

        elif self.state == "playing":
            self.actor.handle_input(message)

        else:
            self.writeln("Invalid state")

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
            self.socket.sendall(self.output_buffer)
            self.output_buffer = ''

    def input_loop(self):
        while self.connected:
            if self.input_buffer:
                next_input = self.input_buffer.pop(0)
                self.handle_input(next_input)
                gevent.sleep(0.5)
            else:
                gevent.sleep(0.05)

    def _run(self):
        self.write_from_template("login")

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
        self.output_buffer += message

    def writeln(self, message=""):
        self.write(message + "\r\n")


class TelnetServer(Greenlet):
    def __init__(self, game):
        super(TelnetServer, self).__init__()
        self.game = game
        self.connections = []

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
        sock.bind(('0.0.0.0', 4200))
        sock.listen(1)

        while self.running:
            conn, addr = sock.accept()
            connection = TelnetConnection(self, conn, addr)
            self.add_connection(connection)
            connection.start()

        sock.shutdown(socket.SHUT_WR)
        sock.close()
