import gevent


class Runnable(object):
    TICK_DELAY = 1.0

    def __init__(self, *args, **kwargs):
        self.running = False

    def start(self, delay=None, count=None):
        self.running = True
        iterations = 0
        while self.running:
            if count is not None:
                iterations += 1
                if iterations > count:
                    self.running = False

            self.tick()
            gevent.sleep(self.TICK_DELAY)

    def tick(self):
        pass

    def stop(self):
        self.running = False
