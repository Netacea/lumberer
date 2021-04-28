import datetime as dt

class BaseSink:
    def add_timestamp(self, logline, timestamp_format="%Y-%m-%dT%H:%M:%S"):
        return logline.replace(
            "timestamp_to_interpolate",
            dt.datetime.now().strftime(timestamp_format)
        )
        