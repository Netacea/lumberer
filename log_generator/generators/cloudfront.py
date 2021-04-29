from generators.base import LogRender


class Cloudfront(LogRender):
    def __init__(self, iterations, realtime, baddata):
        super().__init__(iterations, realtime, baddata)
        self.timestamp_format = "%Y-%m-%d %H:%M:%S"

    def generate(self, d: dict) -> str:
        """Generate Cloudfront Log format string.

        Args:
            d (dict): Dictionary of log components.

        Returns:
            str: Cloudfront Log Line format.
        """
        x_edge_location = "Casdf3-C1"
        cloudfront_host = "d1yn713.cloudfront.net"
        x_edge_result_type = "Miss"
        x_edge_request_id = "S7rh9sTk8_hC6HUOjWRywP4s5Leyg9q_JZd-8P49wQ=="
        x_host_header = "sports.dummydomain.com"
        x_forwarded_for = "-"
        ssl_protocol = "TLSv1.2"
        ssl_cipher = "ECDHE-RSA-AES128-GCM-SHA256"
        x_edge_response_result_type = "Miss"
        fle_status = "-"
        fle_encrypted_fields = "-"
        return f"""{d["timestamp"].strftime(self.timestamp_format)} {x_edge_location} {d["transfer_size"]} {d["ip_address"]} {d["http_method"]} {cloudfront_host} {d["uri_path"]} {d["http_status"]} {d["referer"]} {d["user_agent"]} {d["uri_query_params"]} {d["user_name"]} {x_edge_result_type} {x_edge_request_id} {x_host_header} {d["http_protocol"]} {d["transfer_size"]} {d["request_time"]} {x_forwarded_for} (ssl_protocol) {ssl_cipher} {x_edge_response_result_type} {d["http_protocol"]} {fle_status} {fle_encrypted_fields}
"""  # noqa: E501
