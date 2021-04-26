import sys
from enum import Enum
from typing import Optional

import typer

import generators as lg
import output as sinks


class Sinks(str, Enum):
    s3 = "s3"
    kafka = "kafka"
    stdout = "stdout"


class LogTypes(str, Enum):
    apache = "apache"
    cloudfront = "cloudfront"
    cloudflare = "cloudflare"


app = typer.Typer()


@app.command()
def stream(
    filecontent: Optional[typer.FileText] = typer.Argument(sys.stdin),
    output: Sinks = Sinks.stdout,
):
    """Stream stdin to output sink.
    """
    if output == Sinks.stdout:
        for line in filecontent:
            sys.stdout.write(line)
    elif output == Sinks.kafka:
        with sinks.Kafka(broker="broker:9092", topic="my-topic") as kafka:
            for line in filecontent:
                kafka.send(line)


@app.command()
def generate(
    log_type: LogTypes,
    iterations: int = 1,
):
    """Generates log lines to stdout
    """
    log_generator = getattr(lg, log_type.value)
    with typer.progressbar(range(iterations), file=sys.stderr) as progress:
        for value in progress:
            print(log_generator())


if __name__ == "__main__":
    app()
