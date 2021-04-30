#!/usr/bin/env python3

import sys
from enum import Enum
from typing import Optional

from web import Web

import typer
import generators

from __init__ import version_callback


class AvailableLogTypes(str, Enum):
    apache = "Apache"
    cloudfront = "Cloudfront"
    cloudflare = "Cloudflare"


app = typer.Typer()


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
    baddata: Optional[float] = typer.Option(
        None,
        "-b",
        "--baddata",
        help="Generate percentage of bad data to mix in with good data (e.g. 50 = 50%)",
    ),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),
):
    """Generates log lines to stdout."""

    log_generator = getattr(generators, log_type.value)
    log_generator(iterations=iterations, realtime=realtime, baddata=baddata).render(
        file=sys.stdout, quiet=quiet
    )


if __name__ == "__main__":
    app()
