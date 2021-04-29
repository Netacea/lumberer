#!/usr/bin/env python3

import sys
from enum import Enum
from typing import Optional, List

from web import Web

import typer

import generators
import streams as ImplementedSinks


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
    )
):
    with ImplementedSinks.Stdout(rate=rate, schedule=schedule) as sink:
        [sink.send(line) for line in inputfile]


@app.command("kafka")
def kafka_sinks(
    inputfile: Optional[typer.FileText] = typer.Argument(
        sys.stdin,
        show_default=False,
        help="Path to textfile to stream, defaults to stdin pipe if none given.",
    ),
    broker: List[str] = typer.Option(
        ..., help="Kafka broker to connect to. Use flag multiple times for multiple brokers."
    ),
    topic: str = typer.Option(
        ..., help="Kafka topic to send to."
    ),
    producer: AvailableKafkaProducers = typer.Option(
        AvailableKafkaProducers.kafka_confluent,
        "-p",
        "--producer",
        case_sensitive=False,
        help="Kafka producer implementation to use."
    ),
    rate: Optional[int] = typer.Option(
        None, "-r", "--rate", help="Rate-limit line generation per second."
    ),
    schedule: Optional[typer.FileText] = typer.Option(
        None, "-s", "--schedule", help="Path to json file to schedule rate limits."
    ),
):
    with ImplementedSinks.ConfluentKafka(
                rate=rate, schedule=schedule, broker=broker, topic=topic
    ) as sink:
        [sink.send(line) for line in inputfile]


@app.command("s3")
def s3_sink(
    inputfile: Optional[typer.FileText] = typer.Argument(
        sys.stdin,
        show_default=False,
        help="Path to textfile to stream, defaults to stdin pipe if none given.",
    ),
    bucket: str = typer.Option(
        ..., help="The S3 bucket to write to."
    ),
    prefix: str = typer.Option(
        ..., help="Prefix for the S3 key."
    ),
    rate: Optional[int] = typer.Option(
        None, "-r", "--rate", help="Rate-limit line generation per second."
    ),
    schedule: Optional[typer.FileText] = typer.Option(
        None, "-s", "--schedule", help="Path to json file to schedule rate limits."
    ),
    
):
    with ImplementedSinks.S3(
                bucket=bucket, prefix=prefix, rate=rate, schedule=schedule
    ) as sink:
        [sink.send(line) for line in inputfile]


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
    with ImplementedSinks.Files(rate=rate, schedule=schedule) as sink:
        [sink.send(line) for line in inputfile]



if __name__ == "__main__":
    app()
