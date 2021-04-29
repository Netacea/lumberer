from kafka import KafkaProducer
from kafka.errors import KafkaError
from streams.base import Output


class Kafka(Output):
    def __init__(
        self, broker: list, topic: str, rate: int = None, schedule: dict = None
    ):
        """Kafka sink using the kafka=python library.

        Args:
            broker (list): List of brokers to connect to.
            topic (str): Topic to produce the messages to.
            rate (int, optional): Rate per second to send. Defaults to None.
            schedule (dict, optional): Scheduled rate limits. Defaults to None.
        """
        super().__init__(rate=rate, schedule=schedule)
        self.bootstrap_servers = broker
        self.topic = topic

    def __enter__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers, linger_ms=100
        )
        return self

    def __exit__(self, type, value, traceback):
        try:
            self.producer.flush(10)
        except Exception:
            print("Failed to produce all the messages to Kafka")
            raise

    def _send(self, logline: str):
        try:
            self.producer.send(self.topic, logline.encode("UTF-8"))
        except KafkaError as e:
            print(e)
            raise e
