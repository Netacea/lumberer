import functools as _functools
import threading as _threading
import time


def rate_limited(max_per_second: int):
    """Rate-limits the decorated function locally, for one process."""
    lock = _threading.Lock()
    min_interval = 1.0 / max_per_second

    def decorate(func):
        last_time_called = time.perf_counter()

        @_functools.wraps(func)
        def rate_limited_function(*args, **kwargs):
            lock.acquire()
            nonlocal last_time_called
            try:
                elapsed = time.perf_counter() - last_time_called
                left_to_wait = min_interval - elapsed
                if left_to_wait > 0:
                    time.sleep(left_to_wait)

                return func(*args, **kwargs)
            finally:
                last_time_called = time.perf_counter()
                lock.release()

        return rate_limited_function

    return decorate


class Output:
    def __init__(self, rate: int):
        self.rate = rate

    def send(self, logline):
        # if self.rate:
        func = rate_limited(self.rate)(self._send)
        func(logline)
        # else:
        #     self._send(logline)

    def _send(self, logline):
        raise NotImplementedError
