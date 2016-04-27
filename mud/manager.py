from utils.runnable import Runnable
from mud.mixins.get_game import GetGame


class Manager(Runnable):
    def __init__(self, game, *args, **kwargs):
        super(Manager, self).__init__(*args, **kwargs)
        self.game = game
