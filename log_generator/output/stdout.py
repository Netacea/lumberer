from sys import stdout
from output.base import Output


class Stdout(Output):
    def __init__(self, rate: int = None):
        super().__init__(rate=rate)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        stdout.flush()

    def _send(self, logline: str):
        stdout.write(logline)
