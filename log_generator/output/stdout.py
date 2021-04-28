from output.base import BaseSink
import sys

class Stdout(BaseSink):
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def send(self, logline: str):
        logline = super().add_timestamp(logline)
        sys.stdout.write(logline)