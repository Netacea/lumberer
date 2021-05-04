import queue
from multiprocessing import Event, JoinableQueue, Process
from os import getpid
from time import sleep

from confluent_kafka import (
    OFFSET_BEGINNING,
    Consumer,
    KafkaError,
    Producer,
    TopicPartition,
)
from streams.base import Output


class ConfluentKafka(Output):
    def __init__(
        self, broker: list, topic: str, rate: int = None, schedule: dict = None
    ):
        """Kafka sink using the confluent_kafka library.

        Args:
            broker (list): List of brokers to connect to.
            topic (str): Topic to produce the messages to.
            rate (int, optional): Rate per second to send. Defaults to None.
            schedule (dict, optional): Scheduled rate limits. Defaults to None.
        """
        super().__init__(rate=rate, schedule=schedule)
        self.bootstrap_servers = broker
        self.topic = topic
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

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        try:
            self.producer.flush(10)
        except Exception:
            print("Failed to produce all the messages to Kafka")
            raise

    def _send(self, logline: str):
        try:
            self.producer.produce(self.topic, logline.encode("UTF-8"))
            self.producer.poll(0)
        except BufferError:
            self.producer.poll(10)
            self.producer.produce(self.topic, logline.encode("UTF-8"))


class ConfluentKafkaMP(Output):
    def __init__(
        self,
        broker: list,
        topic: str,
        rate: int = None,
        schedule: dict = None,
        buffer_size: int = 100000,
    ):
        """Kafka sink using the confluent_kafka library and multiprocessing.

        Args:
            broker (list): List of brokers to connect to.
            topic (str): Topic to produce the messages to.
            rate (int, optional): Rate per second to send. Defaults to None.
            schedule (dict, optional): Scheduled rate limits. Defaults to None.
        """
        super().__init__(rate=rate, schedule=schedule)
        self.bootstrap_servers = broker
        self.topic = topic
        self.partition_count = 4
        self.producer_queue = JoinableQueue(maxsize=100)
        self.producer_shutdown = Event()
        config = {
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
        self.producers = [
            Process(
                target=self.producer,
                name=f"producer_{idx}",
                args=(self.producer_queue, self.producer_shutdown, config),
            )
            for idx in range(self.partition_count)
        ]
        self.buffer_size = buffer_size
        self.message_buffer = []
        for proc in self.producers:
            proc.daemon = True
            proc.start()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        try:
            self.producer_queue.put(self.message_buffer)
            while not self.producer_queue.empty():
                sleep(0.2)
            self.producer_shutdown.set()
        except Exception:
            print("Failed to produce all the messages to Kafka")
            raise
        for proc in self.producers:
            proc.join()
            proc.close()

    def producer(self, producer_queue, shutdown, config):
        p = Producer(config)
        while not shutdown.is_set():
            p.poll(0)
            try:
                messages = producer_queue.get(block=True, timeout=0.1)
            except queue.Empty:
                continue
            else:
                for message in messages:
                    try:
                        p.produce(self.topic, message)
                    except BufferError:
                        p.poll(10)
                        p.produce(self.topic, message)
                p.flush(10)
                producer_queue.task_done()

    def _send(self, logline: str):
        self.message_buffer.append(logline)
        if len(self.message_buffer) > self.buffer_size:
            self.producer_queue.put(self.message_buffer)
            self.message_buffer = []
