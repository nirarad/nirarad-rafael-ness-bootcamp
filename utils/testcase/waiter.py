import time


class Waiter:
    def __init__(self, time_to_wait):
        self.wait_time = time_to_wait

    def implicit_wait(self):
        start_time = time.time()
        while True:
            if time.time() - start_time > self.wait_time:
                break
            time.sleep(0.1)
