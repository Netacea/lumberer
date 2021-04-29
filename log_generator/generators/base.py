import datetime as dt
from faker import Faker
from typer import progressbar
import sys


class LogRender:
    def __init__(
        self,
        iterations: int = 1,
        seed: int = 4321,
        realtime: bool = True
    ):
        self.iterations = iterations
        self.realtime = realtime
        self.init_timestamp = dt.datetime.now()
        self.fake = Faker()
        Faker.seed(seed)

    def _seed_data(self, index=None):
        fake = self.fake
        if self.realtime:
            timestamp = dt.datetime.now()
        else:
            timestamp = self.init_timestamp
        return {
            # "index": index,
            "timestamp": timestamp,
            "ip_address": fake.ipv4_public(),
            "user_name": fake.random_element(elements=("-", fake.user_name())),
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

    def render(self, file, quiet):
        def print_line(seed=0):
            x = self._seed_data(seed)
            print(self.generate(x), file=file)

        if quiet:
            for _ in range(self.iterations):
                print_line()
        else:
            with progressbar(
                range(self.iterations),
                label="Progress:",
                file=sys.stderr,
                fill_char="█",
                empty_char=" ",
            ) as progress:
                for value in progress:
                    print_line()
