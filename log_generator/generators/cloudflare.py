from generators.base import LogRender


class Cloudflare(LogRender):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timestamp_format = "%Y-%m-%dT%H:%M:%SZ"

    def generate(self, d: dict) -> str:
        """Generate Cloudflare Log format string.

        Args:
            d (dict): Dictionary of log components.

        Returns:
            str: Cloudflare Log Line format.
        """
        transfer_size = 0 if d["transfer_size"] == "-" else d["transfer_size"]
        log_timestamp = d["timestamp"].strftime(self.timestamp_format)
        log_line = f""""CacheCacheStatus":"hit","CacheResponseBytes":{transfer_size},"CacheResponseStatus":{d["http_status"]},"CacheTieredFill":false,"ClientASN":5607,"ClientCountry":"{d["loc"]}","ClientDeviceType":"mobile","ClientIP":"{d["ip_address"]}","ClientIPClass":"noRecord","ClientRequestBytes":{transfer_size},"ClientRequestHost":"{d["host"]}","ClientRequestMethod":"{d["http_method"]}","ClientRequestProtocol":"{d["http_protocol"]}","ClientRequestReferer":"{d["referer"]}","ClientRequestURI":"{d["uri_path"]}","ClientRequestUserAgent":"{d["user_agent"]}","ClientSSLCipher":"ECDHE-RSA-AES128-GCM-SHA256","ClientSSLProtocol":"TLSv1.2","ClientSrcPort":59400,"EdgeColoID":21,"EdgeEndTimestamp":"{log_timestamp}","EdgePathingOp":"wl","EdgePathingSrc":"macro","EdgePathingStatus":"nr","EdgeRateLimitAction":"","EdgeRateLimitID":0,"EdgeRequestHost":"{d["host"]}","EdgeResponseBytes":{transfer_size},"EdgeResponseCompressionRatio":0,"EdgeResponseContentType":"application/x-javascript;charset=utf-8","EdgeResponseStatus":{d["http_status"]},"EdgeServerIP":"","EdgeStartTimestamp":"{log_timestamp}","OriginIP":"","OriginResponseBytes":0,"OriginResponseHTTPExpires":"","OriginResponseHTTPLastModified":"","OriginResponseStatus":0,"OriginResponseTime":0,"OriginSSLProtocol":"unknown","RayID":"443403c718asdf83","SecurityLevel":"low","WAFAction":"unknown","WAFFlags":"0","WAFMatchedVar":"","WAFProfile":"unknown","WAFRuleID":"","WAFRuleMessage":"","ZoneID":24067324"""  # noqa: E501
        return "{" + log_line + "}"
