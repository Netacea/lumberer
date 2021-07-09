import datetime as dt
from random import choices

from cachetools import TTLCache, cached
from faker import Faker
from loguru import logger
from tqdm import tqdm, trange

# Remove standard handler and write loguru lines via tqdm.write
logger.remove()
logger.add(lambda msg: tqdm.write(msg, end=""))


valid_log_data_cache = TTLCache(1, 0.01)
bad_log_data_cache = TTLCache(1, 1)


class LogRender:
    def __init__(self, **kwargs):
        self.iterations = kwargs.get("iterations")
        self.realtime = kwargs.get("realtime")
        self.junk_percentage = kwargs.get("baddata")
        self.init_timestamp = dt.datetime.now()
        self.fake = Faker()
        Faker.seed(kwargs.get("seed"))

    @staticmethod
    def _seed_data(fake, realtime, timestamp):
        static_data = {
            "host": "example.com",  # fake.domain_name(),
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

    def render(self, **kwargs):
        file = kwargs.get("file")
        quiet = kwargs.get("quiet")
        position = kwargs.get("position")

        def write(data=None):
            if not self.junk_percentage:
                data = self._seed_data(self.fake, self.realtime, self.init_timestamp)
            else:
                if bool(
                    choices(
                        [0, 1],
                        weights=[self.junk_percentage, 100 - self.junk_percentage],
                        k=1,
                    )[0]
                ):
                    data = self._seed_data(
                        self.fake, self.realtime, self.init_timestamp
                    )
                else:
                    data = self._seed_bad_data(
                        self.fake, self.realtime, self.init_timestamp
                    )
            print(self.generate(data), file=file)

        for _ in trange(
            self.iterations,
            disable=quiet,
            unit="lines",
            desc="Generating",
            unit_scale=True,
            position=position,
            mininterval=0.5,
            maxinterval=1,
        ):
            write()
