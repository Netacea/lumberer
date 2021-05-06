from sys import stdout

from streams.base import Output


class Stdout(Output):
    def __init__(self, rate: int, schedule):
        super().__init__(rate=rate, schedule=schedule)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        stdout.flush()

    def _send(self, logline: str):
        stdout.write(logline)
