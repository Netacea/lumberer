import httpx
from streams.base import Output


class HTTP(Output):
    def __init__(self, url: str, rate: int = 1, schedule: dict = None):
        """Synchronous HTTP client for submitting logs.

        Args:
            url (str): URL of endpoint to POST to.
            rate (int, optional): Submissions per second rate limiter. Defaults to 1.
        """
        super().__init__(rate=rate, schedule=schedule)
        self.url = url
        self.client = httpx.Client(http2=True)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.client.close()

    def send(self, logline: str):
        data = {
            "Request": logline,
            "TimeLocal": "2020-09-25 16:30:00:00 +0000",
            "RealIp": "1.1.1.1",
            "UserAgent": "UserAgent Value",
            "Status": "200",
            "RequestTime": "9",
            "BytesSent": "100",
            "NetaceaUserIdCookie": "NzQ5NTkyMDBmNDc5NmJkYzcwZmQ5YzgxYzg4MjI3NTcwZWYwODVkYTc0NGI4YmM3MTFmNjE3YWQzM2UwZTgxMQ==_/@#/1596112893_/@#/m92recxp96jt0vfh_/@#/211;",
            "NetaceaMitigationApplied": "ip_allow",
            "Referer": "-",
        }
        response = self.client.post(self.url, data=data)
