from generators.base import LogRender


class Apache(LogRender):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timestamp_format = "%d/%b/%Y:%H:%M:%S +0000"

    def generate(self, d: dict) -> str:
        """Generate Apache Combined Log format string.

        Args:
            d (dict): Dictionary of log components.

        Returns:
            str: Apache Combined Log Line format.
        """
        return f'{d["ip_address"]} - {d["user_name"]} [{d["timestamp"].strftime(self.timestamp_format)}] "{d["http_method"]} /{d["uri_path"]+d["uri_query_params"]} {d["http_protocol"]}" {d["http_status"]} "{d["referer"]}" "{d["user_agent"]}"'  # noqa: E501
