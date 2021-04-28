import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timezone
from output.base import Output


class S3(Output):
    def __init__(
        self,
        bucket: str,
        prefix: str,
        rate: int = None,
        buffer_size: int = 1000,
        compressed: bool = False,
    ):
        super().__init__(rate=rate)
        self.compressed = compressed
        self.buffer_size = buffer_size
        self.bucket = bucket
        self.prefix = prefix

    def __enter__(self, buffer_size=1000):
        self.buffer = []
        return self

    def __exit__(self, type, value, traceback):
        now = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
        self.write(f"{now}.log")

    def _compress(self, method: str = "gzip"):
        pass

    def _send(self, logline: str):
        self.buffer.append(logline)
        if len(self.buffer) > self.buffer_size:
            now = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
            self.write(f"{now}.log")

    def write(self, key: str):
        with open(key, "w") as file:
            file.write("".join(self.buffer))
        self.buffer = []
