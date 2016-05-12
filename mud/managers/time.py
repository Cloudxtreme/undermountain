from mud.manager import Manager
from mud.entities.character import Character


class TimeManager(Manager):
    TICK_DELAY = 1

    def tick(self):
        for character in Character.query(self.game):
            character.tick()
