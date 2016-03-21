#!/usr/bin/env python
"""
Undermountain Shell Script
Entrypoint into the Application
"""
from mud.engine import Engine
from mud.environment import Environment

VERSION = Engine.get_version()

print("Undermountain v{}".format(VERSION))
print(79 * "=")

ENVIRONMENT = Environment.get('test')

ENGINE = Engine(ENVIRONMENT)
ENGINE.run()
ENGINE.join()
