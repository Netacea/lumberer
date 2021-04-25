import boto3
from botocore.exceptions import ClientError


class S3Writer:
    def __init__(self, compressed: bool = False):
        self.compressed = compressed

    def _compress(self, method: str = "gzip"):
        pass

    def write(self, bucket: str, key: str):
        s3_client = boto3.client("s3")
        pass
