import sys
from enum import Enum
from typing import Optional

import typer

import generators as lg


class Sinks(str, Enum):
    s3 = "s3"
    kafka = "kafka"
    stdout = "stdout"


class LogTypes(str, Enum):
    apache = "apache"


app = typer.Typer()


@app.command()
def stream(
    filecontent: Optional[typer.FileText] = typer.Argument(sys.stdin),
    output: Sinks = Sinks.stdout,
):
    """Stream stdin to output sink.

    Args:
        filecontent (Optional[typer.FileText], optional): Logfile. Defaults to typer.Argument(sys.stdin).
    """
    if output == Sinks.stdout:
        for line in filecontent:
            sys.stdout.write(line)


@app.command()
def generate(
    log_type: LogTypes = None,
    iterations: int = 1,
):
    log_generator = getattr(lg, log_type.value)
    for _ in range(iterations):
        print(log_generator())


if __name__ == "__main__":
    app()
