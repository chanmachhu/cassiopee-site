import time
from collections import deque


class Limiter:
    """In-memory sliding window of one minute. State is per process."""

    def __init__(self, global_per_min=30, per_client_per_min=5, trust_forwarded_for=False, clock=time.monotonic):
        self.global_max = global_per_min
        self.client_max = per_client_per_min
        self.trust = trust_forwarded_for
        self.clock = clock
        self.hits = deque()
        self.clients: dict[str, deque] = {}

    def allow(self, forwarded_for: str | None) -> bool:
        now = self.clock()
        self._expire(self.hits, now)
        if len(self.hits) >= self.global_max:
            return False
        client = None
        # Only meaningful if the real visitor address reaches the app; otherwise anyone can spoof it.
        if self.trust and forwarded_for:
            client = forwarded_for.split(",")[0].strip()
            hits = self.clients.setdefault(client, deque())
            self._expire(hits, now)
            if len(hits) >= self.client_max:
                return False
            hits.append(now)
        self.hits.append(now)
        return True

    @staticmethod
    def _expire(hits: deque, now: float):
        while hits and hits[0] <= now - 60:
            hits.popleft()
