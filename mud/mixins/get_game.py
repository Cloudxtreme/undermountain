import inspect


class GetGame(object):
    @classmethod
    def get_game(cls):
        from mud.game import Game

        caller = cls.get_caller()
        if type(caller) is Game:
            return caller
        return caller.game

    @classmethod
    def get_caller(cls):
        try:
            for frame in inspect.stack():
                obj = frame[0].f_locals.get('self', None)
                if obj is not None:
                    return obj

        except KeyError:
            return None

        return None
