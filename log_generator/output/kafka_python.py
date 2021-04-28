from kafka import KafkaProducer
from kafka.errors import KafkaError
from output.base import BaseSink

class Kafka(BaseSink):
    def __init__(self, broker: list, topic: str):
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

    def send(self, logline: str):
        logline = super().add_timestamp(logline)
        try:
            self.producer.send(self.topic, logline.encode("UTF-8"))
        except KafkaError as e:
            print(e)
            raise e
