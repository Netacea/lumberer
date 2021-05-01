from datetime import datetime, timezone
from pathlib import Path

from streams.base import Output


class Files(Output):
    def __init__(
        self,
        compressed: bool,
        rate: int,
        schedule: dict,
        path: str = ".",
        buffer_size: int = 1000,
    ):
        """Local Filesystem Sink.

        Writes files locally with a given path (must already exist).

        Args:
            path (str, optional): Path to directory you want to stream to. Defaults to ".".
            buffer_size (int, optional): Lines per file. Defaults to 1000.
            compressed (bool, optional): Should the files be compressed or not. Defaults to False.
            rate (int, optional): [description]. Defaults to None.
        """
        super().__init__(rate=rate, schedule=schedule)
        self.compressed = compressed
        self.suffix = ".log.gz" if compressed else ".log"
        self.buffer_size = buffer_size
        self.path = path

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        if len(self.buffer) > 0:
            now = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
            self.write(f"{now}.log")

    def _send(self, logline: str):
        self.buffer.append(logline)
        if len(self.buffer) >= self.buffer_size:
            now = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
            self.write(f"{now}.log")

    def write(self, key: str):
        self._compress(self.buffer)
        with open(Path(self.path) / Path(key).with_suffix(self.suffix), "wb") as file:
            file.write(self.body.getvalue())
        self._reset()
