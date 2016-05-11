"""
MANAGERS
"""
from mud.managers.combat import CombatManager
from mud.managers.time import TimeManager
from mud.managers.save import SaveManager


MANAGER_CLASSES = [
    TimeManager,
    CombatManager,
    SaveManager,
]
