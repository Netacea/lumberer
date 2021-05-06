import functools as _functools
import json
import sys
import threading as _threading
import time
from bz2 import BZ2File
from gzip import GzipFile
from io import BytesIO
from itertools import cycle
from lzma import LZMAFile
from os import close
from sys import exit
from typing import Callable, TextIO

from cachetools import TTLCache, cached

# Remove standard handler and write loguru lines via tqdm.write
from loguru import logger
from tqdm import tqdm
from zstandard import FLUSH_FRAME, ZstdCompressor

logger.remove()
logger.add(lambda msg: tqdm.write(msg, end="", file=sys.stderr))


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
            schedule (dict, optional): Dictionary of scheduled rate limits.
            Defaults to None.
        """
        self._reset()
        self.rate = rate

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

    def _send(self, logline: str):
        raise NotImplementedError

    def _compress(self, method: str = "gzip"):
        def bytes_buffer():
            return "".join(self.buffer).encode("UTF-8")

        if method == "zstd":
            cctx = ZstdCompressor(level=12)
            compressed = cctx.stream_writer(self.body, closefd=False)
            self.suffix = ".log.zstd"
        elif method == "gzip":
            compressed = GzipFile(None, "wb", compresslevel=9, fileobj=self.body)
            self.suffix = ".log.gz"
        elif method == "bzip":
            compressed = BZ2File(self.body, "wb", compresslevel=9)
            self.suffix = ".log.bz2"
        elif method == "lzma":
            compressed = LZMAFile(self.body, "wb")
            self.suffix = ".log.xz"

        compressed.write(bytes_buffer())
        compressed.flush()
        compressed.close()

    def _write(self):
        self.body.write("".join(self.buffer).encode("utf-8"))

    def _reset(self):
        self.ttl = None
        self.buffer = []
        self.body = BytesIO()

    def iterate(self, inputfile: TextIO, position: int):
        [
            self.send(line)
            for line in tqdm(
                inputfile,
                unit=" msgs",
                desc="Streaming",
                unit_scale=True,
                position=position,
                mininterval=0.5,
                maxinterval=1,
                disable=None,
            )
        ]

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
