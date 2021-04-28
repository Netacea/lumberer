from sys import stdout
from streams.base import Output


class Stdout(Output):
    def __init__(self, rate: int = None, scheduling_data=None):
        super().__init__(rate=rate, scheduling_data=scheduling_data)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        stdout.flush()

    def _send(self, logline: str):
        stdout.write(logline)
