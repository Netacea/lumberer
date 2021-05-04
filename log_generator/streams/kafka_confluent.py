import queue
import sys
from multiprocessing import Event, JoinableQueue, Process
from os import getpid
from time import sleep

from confluent_kafka import (
    OFFSET_BEGINNING,
    Consumer,
    KafkaError,
    Producer,
    SerializingProducer,
    TopicPartition,
)
from loguru import logger
from streams.base import Output

logger.remove()
logger.add(sys.stdout, level="DEBUG")


class ConfluentKafka(Output):
    def __init__(
        self,
        broker: list,
        topic: str,
        rate: int,
        schedule: dict,
        sasl_username: str,
        sasl_password: str,
        **kwargs,
    ):
        """Kafka sink using the confluent_kafka library.

        Args:
            broker (list): List of brokers to connect to.
            topic (str): Topic to produce the messages to.
            rate (int): Rate per second to send.
            schedule (dict): Scheduled rate limits.
            sasl_username (str): Optional SASL username.
            sasl_password (str): Optional SASL password.
        """
        super().__init__(rate=rate, schedule=schedule)
        extra_config = kwargs
        if all([sasl_password, sasl_username]):
            extra_config.update(
                {"sasl.username": sasl_username, "sasl.password": sasl_password}
            )
        self.bootstrap_servers = broker
        self.topic = topic
        self.producer = Producer(
            {
                "bootstrap.servers": ",".join(self.bootstrap_servers),
                "linger.ms": 50,
            }
            | extra_config,
            logger=logger,
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

    @staticmethod
    def _acked(err, msg):
        global delivered_records
        """Delivery report handler called on
        successful or failed delivery of message
        """
        if err is not None:
            print("Failed to deliver message: {}".format(err))
        else:
            print(
                "Produced record to topic {} partition [{}] @ offset {}".format(
                    msg.topic(), msg.partition(), msg.offset()
                )
            )

    def _send(self, logline: str):
        try:
            self.producer.produce(self.topic, value=logline)
            self.producer.poll(0)
        except BufferError:
            self.producer.poll(10)
            self.producer.produce(self.topic, value=logline)


class ConfluentKafkaMP(Output):
    def __init__(
        self,
        broker: list,
        topic: str,
        rate: int,
        schedule: dict,
        sasl_username: str,
        sasl_password: str,
        buffer_size: int = 10000,
        **kwargs,
    ):
        """Kafka sink using the confluent_kafka library and multiprocessing.

        Args:
            broker (list): List of brokers to connect to.
            topic (str): Topic to produce the messages to.
            rate (int, optional): Rate per second to send.
            schedule (dict, optional): Scheduled rate limits.
            sasl_username (str): Optional SASL username.
            sasl_password (str): Optional SASL password.
        """
        super().__init__(rate=rate, schedule=schedule)
        extra_config = kwargs
        if all([sasl_password, sasl_username]):
            extra_config.update(
                {"sasl.username": sasl_username, "sasl.password": sasl_password}
            )
        self.bootstrap_servers = broker
        self.topic = topic
        self.partition_count = 4
        self.producer_queue = JoinableQueue(maxsize=100)
        self.producer_shutdown = Event()
        config = {
            "bootstrap.servers": ",".join(self.bootstrap_servers),
            "linger.ms": 50,
        } | extra_config
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
            proc.join(10)
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
