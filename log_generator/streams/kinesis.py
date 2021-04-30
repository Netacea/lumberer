import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timezone
from streams.base import Output


class Kinesis(Output):
    def __init__(self, topic: str, rate: int = None, schedule: dict = None):
        """Kinesis sink using the boto3 library.

        Args:
            topic (str): Topic to produce the messages to.
            rate (int, optional): Rate per second to send. Defaults to None.
            schedule (dict, optional): Scheduled rate limits. Defaults to None.
        """
        super().__init__(rate=rate, schedule=schedule)
        self.topic = topic
        self.client = boto3.client("kinesis")

    def __enter__(self, buffer_size=500):
        self.buffer = []
        return self

    def __exit__(self, type, value, traceback):
        if len(self.buffer) > 0:
            self.write()

    def _send(self, logline: str):
        """Send proxy to write to a buffer until the size is reached.

        Args:
            logline (str): Generated log line to be sent.
        """
        self.buffer.append(
            {"Data": logline.encode("utf-8"), "PartitionKey": logline[:10]}
        )
        if len(self.buffer) >= self.buffer_size:
            self.write()

    def write(self):
        """Write the buffer to Kinesis.

        Raises:
            e: Exception if we fail to send a batch of data.
        """
        try:
            response = self.client.put_records(
                Records=self.buffer, StreamName=self.topic
            )
            if "FailedRecordCount" in response and response["FailedRecordCount"] > 0:
                assert (
                    False
                ), f"""There were {response["FailedRecordCount"]} records failed to go to {self.topic}"""
        except Exception as e:
            print(e)
            raise e

        self.buffer = []