from faker import Faker
from typer import progressbar
import sys


class LogRender:
    def __init__(self, iterations: int = 1, seed: int = 4321):
        self.iterations = iterations
        self.fake = Faker()
        Faker.seed(seed)

    def _seed_data(self, index=None):
        fake = self.fake
        return {
            # "index": index,
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

    def render(self, file):
        with progressbar(
            range(self.iterations),
            label="Progress:",
            file=sys.stderr,
            fill_char="█",
            empty_char=" ",
        ) as progress:
            for value in progress:
                x = self._seed_data(value)
                print(self.generate(x), file=file)
