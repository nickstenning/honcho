from threading import Thread, Timer, Event

class RepeatTimer(Thread):
    def __init__(self, interval, callable, *args, **kwargs):
        Thread.__init__(self)
        self.interval = interval
        self.callable = callable
        self.args = args
        self.kwargs = kwargs
        self.event = Event()
        self.event.set()

    def run(self):
        while self.event.is_set():
            t = Timer(self.interval, self.callable, self.args, self.kwargs)
            t.start()
            t.join()

    def cancel(self):
        self.event.clear()
