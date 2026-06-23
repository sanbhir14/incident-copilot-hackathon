import os
import socket
import time
from contextlib import contextmanager


class DogStatsD:
    def __init__(self) -> None:
        self.host = os.getenv("DD_AGENT_HOST", "127.0.0.1")
        self.port = int(os.getenv("DD_DOGSTATSD_PORT", "8125"))
        self.enabled = bool(os.getenv("DD_API_KEY"))

    def increment(self, metric: str, value: int = 1, tags: list[str] | None = None) -> None:
        self._send(f"{metric}:{value}|c", tags)

    def gauge(self, metric: str, value: float, tags: list[str] | None = None) -> None:
        self._send(f"{metric}:{value}|g", tags)

    def timing_ms(self, metric: str, value: float, tags: list[str] | None = None) -> None:
        self._send(f"{metric}:{value}|ms", tags)

    def _send(self, payload: str, tags: list[str] | None) -> None:
        if not self.enabled:
            return

        if tags:
            payload = f"{payload}|#{','.join(tags)}"

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.sendto(payload.encode("utf-8"), (self.host, self.port))
        finally:
            sock.close()


metrics = DogStatsD()


@contextmanager
def timed_metric(metric_name: str, tags: list[str] | None = None):
    started_at = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        metrics.timing_ms(metric_name, elapsed_ms, tags)

