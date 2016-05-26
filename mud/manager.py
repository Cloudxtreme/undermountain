from utils.runnable import Runnable


class Manager(Runnable):
    def __init__(self, game, *args, **kwargs):
        super(Manager, self).__init__(*args, **kwargs)
        self.game = game
