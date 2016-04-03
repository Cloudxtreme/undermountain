#!/usr/bin/env python
"""
Undermountain Shell Script
Entrypoint into the Application
"""
from mud.environment import Environment
from mud.game import Game
from setproctitle import setproctitle

VERSION = Game.get_version()

print("Undermountain v{}".format(VERSION))
print(79 * "=")

ENVIRONMENT = Environment.get('test')

setproctitle("undermountain: {}".format(ENVIRONMENT.id))

GAME = Game(ENVIRONMENT)
GAME.run()
GAME.join()
