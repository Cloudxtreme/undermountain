from __future__ import absolute_import
import time


class Time(object):
    TIMERS = {}

    @classmethod
    def tick(cls, name=""):
        cls.TIMERS[name] = time.time()

    @classmethod
    def tock(cls, name=""):
        if name not in cls.TIMERS:
            cls.tick()

        print("{}{}".format(
            (name + " ") if name else "",
            (time.time() - cls.TIMERS[name])
        ))
