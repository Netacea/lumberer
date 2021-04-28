import datetime as dt
import functools as _functools
import re
import threading as _threading
import time
from typing import Callable
from random import randint
from cachetools import TTLCache, cached
from itertools import cycle
import json
from sys import exit


def rate_limited(max_per_second: int) -> Callable:
    """Rate limiting decorator

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
    def __init__(self, rate: int = None, scheduling_data=None):
        self.rate = rate
        self.ttl = None
        if scheduling_data:
            self._parse_schedule(scheduling_data)
            self.rate_set = cycle(self.raw_rate)
            self.ttlcache = TTLCache(1, ttl=self.ttl)


    def _parse_schedule(self, scheduling_data):
        try:
            x = json.load(scheduling_data)
            self.raw_rate = x["schedule"]
            self.ttl = x["update_interval"]
        except KeyError:
            print("ERROR: Missing value in json file")
            exit(1)
        except json.decoder.JSONDecodeError:
            print("ERROR: json is malformed")
            exit(2)
        except Exception as e:
            raise e


    def _rate_polling(self):
        if self.rate:
            return self.rate
        else:
            @cached(cache=self.ttlcache)
            def subfunction(self):
                return next(self.rate_set)
            return subfunction(self)

    def _add_timestamp(self, logline: str):
        """Replace the logline's format placeholder with a real timestamp

            Args:
                logline (str): the raw logline before real timestamp is added

            Returns:
                str - the logline with the current timestamp in target format
        """
        target_pattern = r"!!!(.+)!!!"
        try:
            target_format = re.search(target_pattern, logline).groups()[0]
            new_timestamp = dt.datetime.now().strftime(target_format)
            logline = re.sub(target_pattern, new_timestamp, logline)
        except Exception as e:
            print("WARNING: unable to insert real timestamp in line {}".format(logline))
            print(e)
        finally:
            return logline

    def send(self, logline: str):
        """Docstring
        
            Args:
                logline (str): the logline to send

            Returns:
                None
        """
        logline = self._add_timestamp(logline)
        if self.rate or self.ttl:
            func = rate_limited(self._rate_polling())(self._send)
            func(logline)
        else:
            self._send(logline)

    def _send(self, logline: str):
        raise NotImplementedError