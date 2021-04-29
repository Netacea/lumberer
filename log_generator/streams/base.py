import functools as _functools
import json
import threading as _threading
import time
from itertools import cycle
from sys import exit
from typing import Callable

from cachetools import TTLCache, cached


def rate_limited(max_per_second: int) -> Callable:
    """Rate limiting decorator.

    Args:
        max_per_second (int): Rate the decorated function can execute.

    Returns:
        Callable: Decorated function.
    """
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
    def __init__(self, rate: int = None, schedule: dict = None):
        """Base class for all output sinks.

        Handles rate limiting and sending to child classes via the proxy of
        using the send() method externally, and proxying it to _send() methods
        on child classes.

        Args:
            rate (int, optional): Rate limiter per second. Defaults to None.
            schedule (dict, optional): Dictionary of scheduled rate limits. Defaults to None.
        """
        self.rate = rate
        self.ttl = None
        if schedule:
            self._parse_schedule(schedule)
            self.rate_set = cycle(self.raw_rate)
            self.ttlcache = TTLCache(1, ttl=self.ttl)

    def _parse_schedule(self, schedule: dict):
        """Parses schedule json into interval and rates.

        Args:
            schedule (dict): JSON deserialised for scheduling.
        """
        try:
            x = json.load(schedule)
            self.raw_rate = x["schedule"]
            self.ttl = x["update_interval"]
        except KeyError:
            print("ERROR: Missing value in json file")
            exit(1)
        except json.decoder.JSONDecodeError:
            print("ERROR: json is malformed")
            exit(2)

    def _rate_polling(self) -> int:
        """Rate limiting the send method.

        Returns:
            int: Log lines per second
        """
        if self.rate:
            return self.rate
        else:

            @cached(cache=self.ttlcache)
            def subfunction(self):
                return next(self.rate_set)

            return subfunction(self)

    def send(self, logline: str):
        """Sent log line to sink.

        Args:
            logline (str): the logline to send.

        Returns:
            None
        """
        if self.rate or self.ttl:
            func = rate_limited(self._rate_polling())(self._send)
            func(logline)
        else:
            self._send(logline)

    def _send(self, logline: str):
        raise NotImplementedError
