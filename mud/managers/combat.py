from mud.manager import Manager
from mud.entities.combat import Combat


class CombatManager(Manager):
    TICK_DELAY = 0.5

    def tick(self):
        combats = Combat.query()
        print("Number of combats.. {}".format(len(combats)))
        for combat in combats:
            combat.tick()
