from mud.manager import Manager
from mud.entities.combat import Combat


class CombatManager(Manager):
    TICK_DELAY = 5

    def tick(self):
        combats = list(Combat.query(self.game))
        print("Number of combats.. {}".format(len(combats)))
        for combat in combats:
            combat.tick()
