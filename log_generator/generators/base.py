import sys
import datetime as dt
from faker import Faker
from typer import progressbar
from cachetools import TTLCache, cached
from random import choices

valid_log_data_cache = TTLCache(1, 1)
bad_log_data_cache = TTLCache(1, 1)


class LogRender:
    def __init__(
        self, iterations: int, realtime: bool, baddata: float, seed: int = 4321
    ):
        self.iterations = iterations
        self.realtime = realtime
        self.baddata = baddata
        self.init_timestamp = dt.datetime.now()
        self.fake = Faker()
        Faker.seed(seed)

    @staticmethod
    def _seed_data(fake, realtime, timestamp):
        static_data = {
            "host": "www-netacea-com",  # fake.domain_name(),
        }

        @cached(cache=valid_log_data_cache)
        def semi_static_gen(fake, realtime, timestamp):
            if realtime:
                timestamp = dt.datetime.now()

            return {
                "ip_address": fake.ipv4_public(),
                "user_name": fake.random_element(elements=("-", fake.user_name())),
                "http_protocol": fake.random_element(elements=("HTTP/1.1", "HTTP/2.0")),
                "timestamp": timestamp,
                "http_method": fake.http_method(),
                "referer": fake.uri(),
                "user_agent": fake.user_agent(),
                "loc": fake.bank_country().lower(),
            }

        def random_gen(fake, realtime, timestamp):
            return {
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
                "http_status": fake.random_element(
                    elements=(200, 201, 301, 302, 303, 400, 401, 404, 500, 502)
                ),
                "transfer_size": fake.random_element(elements=("-", fake.random_int())),
                "request_time": fake.random_element(
                    elements=("-", round(fake.random.random() / 10, 3))
                ),
                "uuid": fake.uuid4(),
            }

        return (
            static_data
            | semi_static_gen(fake, realtime, timestamp)
            | random_gen(fake, realtime, timestamp)
        )

    @staticmethod
    def _seed_bad_data(fake, realtime, timestamp):
        @cached(cache=bad_log_data_cache)
        def semi_static_gen(fake, realtime, timestamp):
            if realtime:
                timestamp = dt.datetime.now()

            return {
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
                "referer": f"!?£$%^&*()-_{fake.uri()}",
                "user_agent": f"!£$%^&*()-_+{fake.user_agent()}",
                "loc": fake.random_element(elements=("", 100, "123")),
                "host": fake.random_element(
                    elements=(
                        "",
                        123,
                        "!£$%^&*()-_",
                        "www.example.long.url.co.uk.org.biz.tv",
                    )
                ),
            }

        def random_gen(fake, realtime, timestamp):
            return {
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
                "uuid": f"!£$%^&*()-_+{fake.uuid4()}",
            }

        return semi_static_gen(fake, realtime, timestamp) | random_gen(
            fake, realtime, timestamp
        )

    def render(self, file, quiet):
        def print_line(data=None):
            if not self.baddata:
                data = self._seed_data(self.fake, self.realtime, self.init_timestamp)
            else:
                if bool(
                    choices([0, 1], weights=[self.baddata, 100 - self.baddata], k=1)[0]
                ):
                    data = self._seed_data(
                        self.fake, self.realtime, self.init_timestamp
                    )
                else:
                    data = self._seed_bad_data(
                        self.fake, self.realtime, self.init_timestamp
                    )
            print(self.generate(data), file=file)

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
