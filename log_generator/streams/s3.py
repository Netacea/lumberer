from datetime import datetime, timezone

import boto3

# from botocore.exceptions import ClientError
from streams.base import Output


class S3(Output):
    def __init__(
        self,
        bucket: str,
        prefix: str,
        key_line_count: int,
        rate: int = None,
        schedule: dict = None,
        compressed: bool = False,
    ):
        """AWS Simple Storage Service sink using boto3.

        Args:
            bucket (str): Bucket to write to.
            prefix (str): Prefix to add to all the keys.
            rate (int, optional): Ratelimit per second to collect log lines.
            Defaults to None.
            schedule (dict, optional): Scheduled ratelimits. Defaults to None.
            key_line_count (int, optional): Size of files prior to upload in lines.
            Defaults to 1000.
            compressed (bool, optional): Compress the resulting keys. Defaults to False.
        """
        super().__init__(rate=rate, schedule=schedule)
        self.compressed = compressed
        self.buffer_size = key_line_count
        self.bucket = bucket
        self.prefix = prefix
        self.s3 = boto3.client("s3")
        self.suffix = ".log"

    def __enter__(self, buffer_size=1000):
        return self

    def __exit__(self, type, value, traceback):
        if len(self.buffer) > 0:
            now = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
            self.write(f"{now}.log")

    def _send(self, logline: str):
        """Send proxy to write to a buffer until the size is reached.

        Args:
            logline (str): Generated log line to be sent.
        """
        self.buffer.append(logline)
        if len(self.buffer) >= self.buffer_size:
            # TODO - Naming template instead of just using ISO timestamps.
            now = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
            self.write(now)

    def write(self, key: str):
        """Write the buffer to S3.

        Args:
            key (str): File key to write to.
        """
        # TODO - Add error handling in this method.
        if self.compressed:
            self._compress(method="gzip")
        else:
            self._write()
        # s3_object = self.s3.Object(self.bucket, f"{self.prefix}{key}{self.suffix}")
        # s3_object.put(Body="".join(self.buffer))
        self.s3.put_object(
            Bucket=self.bucket,
            Key=f"{self.prefix}{key}{self.suffix}",
            ContentType="text/plain",
            ContentEncoding="gzip" if self.compressed else "utf-8",
            Body=self.body.getvalue(),
        )
        self._reset()
