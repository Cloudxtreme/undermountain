#!/usr/bin/env python
"""
Undermountain Shell Script
Entrypoint into the Application
"""
from mud.environment import Environment
from mud.game import Game

VERSION = Game.get_version()

print("Undermountain v{}".format(VERSION))
print(79 * "=")

ENVIRONMENT = Environment.get('test')

GAME = Game(ENVIRONMENT)
GAME.run()
GAME.join()
