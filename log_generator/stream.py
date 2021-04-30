#!/usr/bin/env python3

import sys
from enum import Enum
from typing import List, Optional

import typer
from loguru import logger
from tqdm import tqdm, trange

import streams as ImplementedSinks
from web import Web

# Remove standard handler and write loguru lines via tqdm.write
logger.remove()
logger.add(lambda msg: tqdm.write(msg, end="", file=sys.stderr))


class AvailableKafkaProducers(str, Enum):
    kafka_python = "kafka-python"
    kafka_confluent = "kafka-confluent"
    kafka_confluent_mp = "kafka-confluent-multiprocessing"


app = typer.Typer()


@app.command("stdout")
def stdout_sink(
    inputfile: Optional[typer.FileText] = typer.Argument(
        sys.stdin,
        show_default=False,
        help="Path to textfile to stream, defaults to stdin pipe if none given.",
    ),
    rate: Optional[int] = typer.Option(
        None, "-r", "--rate", help="Rate-limit line generation per second."
    ),
    schedule: Optional[typer.FileText] = typer.Option(
        None, "-s", "--schedule", help="Path to json file to schedule rate limits."
    ),
):
    # Set the progress bar position based on if the input is stdin
    position = 1 if inputfile is sys.stdin else 0

    with ImplementedSinks.Stdout(rate=rate, schedule=schedule) as sink:
        [
            sink.send(line)
            for line in tqdm(
                inputfile,
                unit=" msgs",
                desc="Streaming",
                unit_scale=True,
                position=position,
            )
        ]


@app.command("kafka")
def kafka_sinks(
    inputfile: Optional[typer.FileText] = typer.Argument(
        sys.stdin,
        show_default=False,
        help="Path to textfile to stream, defaults to stdin pipe if none given.",
    ),
    broker: List[str] = typer.Option(
        ...,
        help="Kafka broker to connect to. Use flag multiple times for multiple brokers.",
    ),
    topic: str = typer.Option(..., help="Kafka topic to send to."),
    producer: AvailableKafkaProducers = typer.Option(
        AvailableKafkaProducers.kafka_confluent,
        "-p",
        "--producer",
        case_sensitive=False,
        help="Kafka producer implementation to use.",
    ),
    rate: Optional[int] = typer.Option(
        None, "-r", "--rate", help="Rate-limit line generation per second."
    ),
    schedule: Optional[typer.FileText] = typer.Option(
        None, "-s", "--schedule", help="Path to json file to schedule rate limits."
    ),
):
    # Set the progress bar position based on if the input is stdin
    position = 1 if inputfile is sys.stdin else 0

    if producer == AvailableKafkaProducers.kafka_confluent:
        sink = ImplementedSinks.ConfluentKafka(
            rate=rate, schedule=schedule, broker=broker, topic=topic
        )
    if producer == AvailableKafkaProducers.kafka_confluent_mp:
        sink = ImplementedSinks.ConfluentKafkaMP(
            rate=rate, schedule=schedule, broker=broker, topic=topic
        )
    if producer == AvailableKafkaProducers.kafka_python:
        sink = ImplementedSinks.Kafka(
            rate=rate, schedule=schedule, broker=broker, topic=topic
        )

    [
        sink.send(line)
        for line in tqdm(
            inputfile,
            unit=" msgs",
            desc="Streaming",
            unit_scale=True,
            position=position,
        )
    ]
    sink.close()


@app.command("s3")
def s3_sink(
    inputfile: Optional[typer.FileText] = typer.Argument(
        sys.stdin,
        show_default=False,
        help="Path to textfile to stream, defaults to stdin pipe if none given.",
    ),
    bucket: str = typer.Option(..., help="The S3 bucket to write to."),
    prefix: str = typer.Option(..., help="Prefix for the S3 key."),
    rate: Optional[int] = typer.Option(
        None, "-r", "--rate", help="Rate-limit line generation per second."
    ),
    schedule: Optional[typer.FileText] = typer.Option(
        None, "-s", "--schedule", help="Path to json file to schedule rate limits."
    ),
):
    # Set the progress bar position based on if the input is stdin
    position = 1 if inputfile is sys.stdin else 0

    with ImplementedSinks.S3(
        bucket=bucket, prefix=prefix, rate=rate, schedule=schedule
    ) as sink:
        [
            sink.send(line)
            for line in tqdm(
                inputfile,
                unit=" msgs",
                desc="Streaming",
                unit_scale=True,
                position=position,
            )
        ]


@app.command("files")
def files_sink(
    inputfile: Optional[typer.FileText] = typer.Argument(
        sys.stdin,
        show_default=False,
        help="Path to textfile to stream, defaults to stdin pipe if none given.",
    ),
    rate: Optional[int] = typer.Option(
        None, "-r", "--rate", help="Rate-limit line generation per second."
    ),
    schedule: Optional[typer.FileText] = typer.Option(
        None, "-s", "--schedule", help="Path to json file to schedule rate limits."
    ),
):
    # Set the progress bar position based on if the input is stdin
    position = 1 if inputfile is sys.stdin else 0

    with ImplementedSinks.Files(rate=rate, schedule=schedule) as sink:
        [
            sink.send(line)
            for line in tqdm(
                inputfile,
                unit=" msgs",
                desc="Streaming",
                unit_scale=True,
                position=position,
            )
        ]


if __name__ == "__main__":
    app()
