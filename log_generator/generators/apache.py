from generators.base import LogRender


class Apache(LogRender):
    def __init__(self, iterations):
        super().__init__(iterations)

    def generate(self, d):
        return f'{d["ip_address"]} - {d["user_name"]} [{d["date_time"].strftime("%d/%b/%Y:%H:%M:%S +0000")}] "{d["http_method"]} {d["uri_path"]+d["uri_query_params"]} {d["http_protocol"]}" {d["http_status"]} "{d["referer"]}" "{d["user_agent"]}"'
