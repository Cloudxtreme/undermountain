# Undermountain Python MUD Engine

A Python-based ROT replacement for Waterdeep.

## Immediate TODOS

- Make this README's commands actually work

  - Create
  - Start
  - Backup
  - Restore
  - Destoy

- Design hot reboots to keep people connected but load new modules
- Create basic telnet server
- Create basic object, actor, room, area
- Create basic event system with blocking
- Create basic subroutine engine for actor, room, object, area, world
- Create data store (with persistent information?)

## Creating An Environment

1. git clone repository
2. cd undermountain
3. virtualenv venv
4. source venv/bin/activate
5. pip install -r requirements.txt
6. ./undermountain create <environment>

## Starting the Environment

1. source venv/bin/activate
2. ./undermountain start <environment>

## Backup an Environment

1. source venv/bin/activate
2. ./undermountain backup <environment> [filename]

## Restore an Environment

1. source venv/bin/activate
2. ./undermountain restore <environment> <filename>

## Destroying an Environment

1. source venv/bin/activate
2. ./undermountain destroy <environment>
