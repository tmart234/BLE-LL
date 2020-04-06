from threading import Timer


class LLTimer():
    def __init__(self, timer_name=None, seconds=None, callback=None):
        self.timers = None
        if self.timer_name and self.seconds is not None:
            self.start_timeout(timer_name, seconds, callback)

    def start_timeout(self, timer_name, seconds, callback):
        disable_timeout(timer_name)
        if callback is None:
            callback = timer_name
        timer = Timer(seconds, callback)
        timer.daemon = True
        timer.setName(timer_name)
        timer.start()
        self.timers[timer_name] = timer

    def update_timeout(self, timer_name):
        if timer_name in self.timers:
            timer = self.timers[timer_name]
            if timer:
                timer.cancel()
                start_timeout(timer_name, timer.interval, timer.function)

    def disable_timeout(self, timer_name):
        if timer_name in self.timers:
            timer = self.timers[timer_name]
            if timer:
                timer.cancel()
                self.timers[timer_name] = None
