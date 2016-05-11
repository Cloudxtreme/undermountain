from mud.manager import Manager
from mud.entities.combat import Combat


class SaveManager(Manager):
    TICK_DELAY = 5

    def tick(self):
        for player in self.game.query_characters():
            connection = player.get_connection()

            if not connection.is_playing():
                continue

            player.save()
