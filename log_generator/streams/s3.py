import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timezone
from streams.base import Output


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
        self.s3 = boto3.resource("s3")

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
        s3_object = self.s3.Object(self.bucket, f"{self.prefix}{key}")
        s3_object.put(Body="".join(self.buffer))
