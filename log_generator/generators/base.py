import datetime as dt
from faker import Faker
from typer import progressbar
import sys


class LogRender:
    def __init__(
        self,
        iterations: int,
        realtime: bool,
        baddata: bool,
        seed: int = 4321,
    ):
        self.iterations = iterations
        self.realtime = realtime
        self.baddata = baddata
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
            "host": fake.domain_name(),
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
            "request_time": fake.random_element(
                elements=("-", round(fake.random.random() / 10, 3))
            ),
            "referer": fake.uri(),
            "user_agent": fake.user_agent(),
            "uuid": fake.uuid4(),
            "loc": fake.bank_country().lower(),
        }

    def _seed_bad_data(self, index=None):
        fake = self.fake
        if self.realtime:
            timestamp = dt.datetime.now()
        else:
            timestamp = self.init_timestamp
        return {
            # "index": index,
            "timestamp": timestamp,
            "ip_address": fake.random_element(
                elements=("", "NOT-AN-IP", "256.500.301.9000", "1")
            ),
            "user_name": fake.random_element(
                elements=("-", "bad-username", "a-really-long-username" * 256)
            ),
            "http_method": fake.random_element(
                elements=("THROW", "EAT", "DRINK", "BLAH")
            ),
            "host": fake.random_element(
                elements=(
                    "",
                    123,
                    "!£$%^&*()-_",
                    "www.example.long.url.co.uk.org.biz.tv",
                )
            ),
            "uri_path": f"!?£$%^&*()-_{fake.uri_path()}",
            "uri_query_params": fake.random_element(
                elements=(
                    "",
                    "!!a=1,b=2,c=3",
                    "%cat=lovely",
                    "-----=two&f=1",
                    "$$end=1",
                    "^^q=2",
                )
            ),
            "http_protocol": fake.random_element(elements=("HTTP/5.0", "PTTH/0.1")),
            "http_status": fake.random_element(
                elements=(1, 25, 91, 602, 603, 700, 701, 804, 900, 1000)
            ),
            "transfer_size": fake.random_element(
                elements=("-", "not-a-number", fake.binary(length=64))
            ),
            "request_time": fake.random_element(
                elements=(
                    "-",
                    "",
                    "long_time",
                    f'!"£$%^&*()-_{round(fake.random.random() / 10, 3)}',
                )
            ),
            "referer": f"!?£$%^&*()-_{fake.uri()}",
            "user_agent": f"!£$%^&*()-_+{fake.user_agent()}",
            "uuid": f"!£$%^&*()-_+{fake.uuid4()}",
            "loc": fake.random_element(elements=("", 100, "123")),
        }

    def render(self, file, quiet):
        def print_line(seed=0):
            x = None
            if not self.baddata:
                x = self._seed_data(seed)
            else:
                x = self._seed_bad_data(seed)
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
