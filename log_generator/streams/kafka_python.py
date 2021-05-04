from kafka import KafkaProducer
from kafka.errors import KafkaError
from streams.base import Output


class Kafka(Output):
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
        """Kafka sink using the kafka=python library.

        Args:
            broker (list): List of brokers to connect to.
            topic (str): Topic to produce the messages to.
            rate (int, optional): Rate per second to send.
            schedule (dict, optional): Scheduled rate limits.
            sasl_username (str): Optional SASL username.
            sasl_password (str): Optional SASL password.
        """
        super().__init__(rate=rate, schedule=schedule)
        extra_config = {k.replace(".", "_"): v for k, v in kwargs.items()}
        if all([sasl_password, sasl_username]):
            extra_config.update(
                {
                    "sasl_plain_username": sasl_username,
                    "sasl_plain_password": sasl_password,
                }
            )
        self.bootstrap_servers = broker
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers, linger_ms=50, **extra_config
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
            self.producer.send(self.topic, logline.encode("UTF-8"))
        except KafkaError as e:
            print(e)
            raise e
