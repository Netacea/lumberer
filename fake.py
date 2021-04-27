from ast import Str
from faker import Faker
import json
import typer
import os
from typing import Optional
from pathlib import Path
from enum import Enum
import sys

app = typer.Typer()


# class LOG_TYPES(str, Enum):
#     apache_combined = "apache_combined"


class LogRender:
    def __init__(self, iterations, output):
        self.iterations = iterations
        self.output_path = output
        self.output_file = None
        self.fake = Faker()
        Faker.seed(4321)

    def __enter__(self):
        self.output_file = open(self.output_path, "w")
        self.uuid_file = open(self.output_path.parent /
                              (self.output_path.name + '.uuid'), "w")
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.output_file.close()
        self.uuid_file.close()

    def render(self, method_name):
        typer.echo(
            f'Generating {self.iterations} log lines of format "{method_name}" to {self.output_path}'
        )
        func = getattr(self, method_name)  # find method that located within the class

        with typer.progressbar(
            range(self.iterations), label="Log Lines Generated", file=sys.stderr
        ) as progress:
            for value in progress:
                x = self._seed_data(value)
                print((func(x)), file=self.output_file)
                print(f'{value+1},{x["uuid"]}', file=self.uuid_file)

    def apache_combined(self, d):
        return f'{d["ip_address"]} - {d["user_name"]} [{d["date_time"].strftime("%d/%b/%Y:%H:%M:%S +0000")}] "{d["http_method"]} {d["uri_path"]+d["uri_query_params"]} {d["http_protocol"]}" {d["http_status"]} "{d["referer"]}" "{d["user_agent"]}"'

    def _seed_data(self, index):
        fake = self.fake
        return {
            "index": index,
            "ip_address": fake.ipv4_public(),
            "user_name": fake.random_element(elements=("-", fake.user_name())),
            "date_time": fake.date_time(),
            "http_method": fake.http_method(),
            "uri_path": fake.uri_path(),
            "uri_query_params": fake.random_element(
                elements=(
                    "",
                    "?a=1,b=2,c=3",
                    "?cat=lovely",
                    "?e=two&f=1",
                    "?end=1",
                    "?q=2",
                )
            ),
            "http_protocol": fake.random_element(elements=("HTTP/1.1", "HTTP/2.0")),
            "http_status": fake.random_element(
                elements=(200, 201, 301, 302, 303, 400, 401, 404, 500, 502)
            ),
            "transfer_size": fake.random_element(elements=("-", fake.random_int())),
            "referer": fake.uri(),
            "user_agent": fake.user_agent(),
            "uuid": fake.uuid4(),
        }


LOG_TYPES = Enum(
    "LOG_TYPES",
    [
        (method.upper(), method)
        for method in dir(LogRender)
        if method.startswith("_") is False and method != "render"
    ],
)


@app.command()
def generate(
    logtype: LOG_TYPES = typer.Option("apache_combined", case_sensitive=False),
    iterations: int = 1,
    outputfile: Path = typer.Option(
        ...,
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        readable=True,
        resolve_path=True,
    ),
):
    with LogRender(iterations=iterations, output=outputfile) as renderer:
        renderer.render(logtype.value)


if __name__ == "__main__":
    app()
