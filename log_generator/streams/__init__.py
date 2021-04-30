"""Streaming output Sinks

This module exposes sinks for the streaming utility to write to.
"""

from streams.kafka_python import Kafka
from streams.kafka_confluent import ConfluentKafka, ConfluentKafkaMP
from streams.s3 import S3
from streams.kinesis import Kinesis
from streams.files import Files
from streams.stdout import Stdout

__all__ = [Kafka, ConfluentKafka, ConfluentKafkaMP, S3, Kinesis, Files, Stdout]
