import sys
from enum import Enum
from typing import Optional

from web import Web

import typer

import generators
import streams as ImplementedSinks


class AvailableSinks(str, Enum):
    s3 = "s3"
    kafka = "kafka"
    confluent = "confluent"
    confluentmp = "confluentmp"
    stdout = "stdout"
    files = "files"


class AvailableLogTypes(str, Enum):
    apache = "Apache"
    cloudfront = "Cloudfront"
    cloudflare = "Cloudflare"


app = typer.Typer()


def version_callback(value: bool):
    if value:
        from __init__ import __version__

        typer.echo(f"Netacea Super Log Generator Version: {__version__}")
        raise typer.Exit()


@app.command()
def stream(
    inputfile: Optional[typer.FileText] = typer.Argument(
        sys.stdin,
        show_default=False,
        help="Path to textfile to stream, defaults to stdin pipe if none given.",
    ),
    outputsink: AvailableSinks = typer.Option(
        AvailableSinks.stdout,
        "-o",
        "--output",
        case_sensitive=False,
        help="Sink to stream data to.",
    ),
    rate: Optional[int] = typer.Option(
        None, "-r", "--rate", help="Rate-limit line generation per second."
    ),
    schedule: Optional[typer.FileText] = typer.Option(
        None, "-s", "--schedule", help="Path to json file to schedule rate limits."
    ),
    version: Optional[bool] = typer.Option(
        None,
        "-v",
        "--version",
        is_eager=True,
        callback=version_callback,
        help="Show tool version.",
    ),
):
    """This tool takes text input, new line seperated and streams it to a sink."""
    with Web():
        if outputsink == AvailableSinks.stdout:
            with ImplementedSinks.Stdout(rate=rate, schedule=schedule) as sink:
                [sink.send(line) for line in inputfile]
        elif outputsink == AvailableSinks.kafka:
            with ImplementedSinks.Kafka(
                rate=rate, schedule=schedule, broker=["broker:9092"], topic="my-topic"
            ) as sink:
                [sink.send(line) for line in inputfile]
        elif outputsink == AvailableSinks.confluent:
            with ImplementedSinks.ConfluentKafka(
                rate=rate, schedule=schedule, broker=["broker:9092"], topic="my-topic"
            ) as sink:
                [sink.send(line) for line in inputfile]
        elif outputsink == AvailableSinks.confluentmp:
            with ImplementedSinks.ConfluentKafkaMP(
                rate=rate, schedule=schedule, broker=["broker:9092"], topic="my-topic"
            ) as sink:
                [sink.send(line) for line in inputfile]
        elif outputsink == AvailableSinks.s3:
            with ImplementedSinks.S3(
                rate=rate, schedule=schedule, bucket="test", prefix="/test"
            ) as sink:
                [sink.send(line) for line in inputfile]
        elif outputsink == AvailableSinks.files:
            with ImplementedSinks.Files(rate=rate, schedule=schedule) as sink:
                [sink.send(line) for line in inputfile]


@app.command()
def generate(
    log_type: AvailableLogTypes = typer.Option(
        ..., "-l", "--logtype", case_sensitive=False, help="Type of log to generate."
    ),
    iterations: int = typer.Option(
        1, "-i", "--iterations", help="Iterations of log lines to generate."
    ),
    quiet: Optional[bool] = typer.Option(
        False, "-q", "--quiet", help="Hide the progress bar."
    ),
    realtime: Optional[bool] = typer.Option(
        False, "-r", "--realtime", help="Interpolate current timestamps in log lines."
    ),
    version: Optional[bool] = typer.Option(
        None,
        "-v",
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show tool version.",
    ),
):
    """Generates log lines to stdout."""

    log_generator = getattr(generators, log_type.value)
    log_generator(iterations=iterations).render(file=sys.stdout, quiet=quiet)


if __name__ == "__main__":
    app()
