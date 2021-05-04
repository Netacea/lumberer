#!/usr/bin/env python3

import sys
from enum import Enum
from pathlib import Path
from typing import List, Optional

import streams as ImplementedSinks
import typer


class AvailableKafkaProducers(str, Enum):
    kafka_python = "kafka-python"
    kafka_confluent = "kafka-confluent"
    kafka_confluent_mp = "kafka-confluent-multiprocessing"


class FilesCompressors(Enum):
    bzip = "bzip"
    gzip = "gzip"
    lzma = "lzma"
    zstd = "zstd"


app = typer.Typer(add_completion=False)


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
    position: Optional[int] = typer.Option(
        0,
        "-p",
        "--position",
        help="Position for progress bar, use 1 if you're piping from generate.",
    ),
):
    # Set the progress bar position based on if the input is stdin
    with ImplementedSinks.Stdout(rate=rate, schedule=schedule) as sink:
        sink.iterate(inputfile, position)


@app.command("kafka")
def kafka_sinks(
    inputfile: Optional[typer.FileText] = typer.Argument(
        sys.stdin,
        show_default=False,
        help="Path to textfile to stream, defaults to stdin pipe if none given.",
    ),
    broker: List[str] = typer.Option(
        ...,
        help="Kafka broker to connect to. Can be used multiple times.",
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
    position: Optional[int] = typer.Option(
        0,
        "-p",
        "--position",
        help="Position for progress bar, use 1 if you're piping from generate.",
    ),
):
    # Set the progress bar position based on if the input is stdin
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

    sink.iterate(inputfile, position)
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
    position: Optional[int] = typer.Option(
        0,
        "-p",
        "--position",
        help="Position for progress bar, use 1 if you're piping from generate.",
    ),
    key_line_count: Optional[int] = typer.Option(
        1000, "-c", "--linecount", help="Max line count size per S3 key."
    ),
):
    # Set the progress bar position based on if the input is stdin
    with ImplementedSinks.S3(
        bucket=bucket,
        prefix=prefix,
        rate=rate,
        schedule=schedule,
        key_line_count=key_line_count,
    ) as sink:
        sink.iterate(inputfile, position)


@app.command("kinesis")
def kinesis_sink(
    inputfile: Optional[typer.FileText] = typer.Argument(
        sys.stdin,
        show_default=False,
        help="Path to textfile to stream, defaults to stdin pipe if none given.",
    ),
    stream: str = typer.Option(..., help="Kinesis stream name to send to."),
    rate: Optional[int] = typer.Option(
        None, "-r", "--rate", help="Rate-limit line generation per second."
    ),
    schedule: Optional[typer.FileText] = typer.Option(
        None, "-s", "--schedule", help="Path to json file to schedule rate limits."
    ),
    position: Optional[int] = typer.Option(
        0,
        "-p",
        "--position",
        help="Position for progress bar, use 1 if you're piping from generate.",
    ),
):
    # Set the progress bar position based on if the input is stdin
    with ImplementedSinks.Kinesis(
        stream=stream,
        rate=rate,
        schedule=schedule,
    ) as sink:
        sink.iterate(inputfile, position)


@app.command("files")
def files_sink(
    inputfile: Optional[typer.FileText] = typer.Argument(
        sys.stdin,
        show_default=False,
        help="Path to textfile to stream, defaults to stdin pipe if none given.",
    ),
    compressed: Optional[FilesCompressors] = typer.Option(
        None, "-c", "--compressor", help="Write compressed logs."
    ),
    rate: Optional[int] = typer.Option(
        None, "-r", "--rate", help="Rate-limit line generation per second."
    ),
    schedule: Optional[typer.FileText] = typer.Option(
        None, "-s", "--schedule", help="Path to json file to schedule rate limits."
    ),
    position: Optional[int] = typer.Option(
        0,
        "-p",
        "--position",
        help="Position for progress bar, use 1 if you're piping from generate.",
    ),
    path: Optional[Path] = typer.Option(Path("."), help="Where to write the files to."),
    line_count: Optional[int] = typer.Option(
        1000, "-c", "--linecount", help="Max line count size per file."
    ),
):
    # Set the progress bar position based on if the input is stdin
    with ImplementedSinks.Files(
        rate=rate,
        schedule=schedule,
        compressed=compressed,
        path=path,
        linecount=line_count,
    ) as sink:
        sink.iterate(inputfile, position)


if __name__ == "__main__":
    app()
