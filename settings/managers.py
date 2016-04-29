"""
MANAGERS
"""
from mud.managers.combat import CombatManager
from mud.managers.time import TimeManager


MANAGER_CLASSES = [
    TimeManager,
    CombatManager,
]
