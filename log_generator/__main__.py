import datetime as dt
import sys
from enum import Enum
from typing import Optional

from typer.params import Option
from web import Web

import typer

import generators
import streams as ImplementedSinks


class AvailableSinks(str, Enum):
    s3 = "s3"
    kafka = "kafka"
    confluent = "confluent"
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

        typer.echo(f"Netacea Log Generator Version: {__version__}")
        raise typer.Exit()


@app.command()
def stream(
    file: Optional[typer.FileText] = typer.Argument(sys.stdin),
    output: AvailableSinks = typer.Option(AvailableSinks.stdout, case_sensitive=False),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),
    rate: Optional[int] = typer.Option(None),
    scheduling_data: Optional[typer.FileText] = typer.Option(None)
):
    """Stream stdin to output sink."""
    with Web():
<<<<<<< HEAD
        if output == Sinks.stdout:
            with sinks.Stdout() as stdout:
                for line in file:
                    stdout.send(line)
        elif output == Sinks.kafka:
            with sinks.Kafka(broker=["broker:9092"], topic="my-topic") as kafka:
                for line in file:
                    kafka.send(line)
        elif output == Sinks.confluent:
            with sinks.ConfluentKafka(broker=["broker:9092"], topic="my-topic") as ck:
                for line in file:
                    ck.send(line)
        elif output == Sinks.s3:
            with sinks.S3(bucket="test", prefix="/test") as s3:
                for line in file:
                    s3.send(line)
        elif output == Sinks.files:
            with sinks.Files() as local:
                for line in file:
                    local.send(line)
=======
        if output == AvailableSinks.stdout:
            with ImplementedSinks.Stdout(rate=rate, scheduling_data=scheduling_data) as sink:
                [sink.send(line) for line in file]
        elif output == AvailableSinks.kafka:
            with ImplementedSinks.Kafka(rate=rate, broker="broker:9092", topic="my-topic") as sink:
                [sink.send(line) for line in file]
        elif output == AvailableSinks.s3:
            with ImplementedSinks.S3(rate=rate, bucket="test", prefix="/test") as sink:
                [sink.send(line) for line in file]
        elif output == AvailableSinks.files:
            with ImplementedSinks.Files(rate=rate) as sink:
                [sink.send(line) for line in file]
>>>>>>> confluent


@app.command()
def generate(
    log_type: AvailableLogTypes = typer.Option(..., case_sensitive=False),
    iterations: int = 1,
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),
    quiet: Optional[bool] = typer.Option(False)
):
    """Generates log lines to stdout"""

    log_generator = getattr(generators, log_type.value)
    log_generator(iterations=iterations).render(file=sys.stdout, quiet=quiet)


if __name__ == "__main__":
    app()
