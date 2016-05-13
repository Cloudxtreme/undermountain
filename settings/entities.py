"""
ENTITIES

The types of "things" that can be in the World.  Must be registered, as we
instantiate their factories in the Game to be added/removed.
"""

from mud.entities.area import Area
from mud.entities.room import Room
from mud.entities.actor import Actor
from mud.entities.object import Object
from mud.entities.character import Character

ENTITIES = [
    Area,
    Room,
    Actor,
    Object,
    Character,
]
