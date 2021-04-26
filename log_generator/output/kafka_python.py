from kafka import KafkaProducer
from kafka.errors import KafkaError


class Kafka:
    def __init__(self, broker: list, topic: str):
        self.bootstrap_servers = broker
        self.topic = topic

    def __enter__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers, linger_ms=100)
        return self

    def __exit__(self, type, value, traceback):
        self.producer.flush(10)

    def send(self, logline: str):
        self.producer.send(self.topic, logline.encode("UTF-8"))
