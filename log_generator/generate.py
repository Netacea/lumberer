#!/usr/bin/env python3

import sys
from enum import Enum
from typing import Optional

import generators
import typer
from __init__ import version_callback


class AvailableLogTypes(str, Enum):
    apache = "Apache"
    cloudfront = "Cloudfront"
    cloudflare = "Cloudflare"


app = typer.Typer(add_completion=False)


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
    seed: Optional[int] = typer.Option(
        4321, "-s", "--seed", help="Reproducible seed to generate fake data with."
    ),
    position: Optional[int] = typer.Option(
        0,
        "-p",
        "--position",
        help="Position for progress bar, use 1 if you're piping from generate.",
    ),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),
):
    """Generates log lines to stdout."""

    log_generator = getattr(generators, log_type.value)
    log_generator(
        iterations=iterations, realtime=realtime, baddata=baddata, seed=seed
    ).render(file=sys.stdout, quiet=quiet, position=position)


if __name__ == "__main__":
    app()
