from confluent_kafka import (
    OFFSET_BEGINNING,
    Consumer,
    KafkaError,
    Producer,
    TopicPartition,
)

from output.base import BaseSink


class ConfluentKafka(BaseSink):
    def __init__(self, broker: list, topic: str):
        self.bootstrap_servers = broker
        self.topic = topic

    def __enter__(self):
        self.producer = Producer(
            {
                "bootstrap.servers": ",".join(self.bootstrap_servers),
                "batch.num.messages": 2000,
                "queue.buffering.max.ms": 1000,
                "batch.size": 32768,
                # "linger.ms": 1000,
                # "max.in.flight.requests.per.connection": 10,
                # "queue.buffering.backpressure.threshold": 2,
                # "statistics.interval.ms": 10000,
                # "stats_cb": logger.debug,
                # "throttle_cb": logger.debug,
            }
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
            self.producer.produce(self.topic, logline.encode("UTF-8"))
            self.producer.poll(0)
        except BufferError:
            self.producer.poll(10)
            self.producer.produce(self.topic, logline.encode("UTF-8"))
