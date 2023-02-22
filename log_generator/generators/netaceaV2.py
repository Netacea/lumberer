from generators.base import LogRender
import json


class NetaceaV2(LogRender):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timestamp_format = "%FT%T%z"

    def generate(self, d: dict) -> str:
        request = f"""{d.method} {d.uri_path}{d.query_params} ${d.http_protocol}"""
        time_tuple = d.timestamp.timetuple()
        log_line: dict = {
            "status": str(d.http_status),
            "referrer": d.referer,
            "request": request,
            "request_time": d.request_time,
            "integration_type": "lumbererType",
            "integration_version": "lumbererVersion",
            "client": d.ip_address,
            "user_agent": d.user_agent,
            "hour": time_tuple.tm_hour,
            "minute": time_tuple.tm_min,
            "@timestamp": d.timestamp.strftime(self.timestamp_format),
            "path": d.uri_path,
            "protocol": d.http_protocol,
            "query": d.query_params,
            "user_id": d.uuid,
        }
        # v2 log lines come through as batches
        return json.dumps([log_line])
