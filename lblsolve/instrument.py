import time

class Stopwatch:
    def __init__(self):
        self.running_time = 0
        self.mark = time.time()

    def checkpoint(self):
        stopped = time.time()
        self.running_time += stopped - self.mark
        self.mark = stopped

