import time

import math

def memory_chunk(size_in_kb):
    l = []
    for i in range(0, int(math.ceil(size_in_kb))):
        l.append("*" * 1024)  # 1KB
    return l

class FakeConnection:

    def __init__(self, latency_ms, bandwidth_kbps):
        self._latency_ms = latency_ms

        self._bandwidth_kbps = bandwidth_kbps
        self._kbytes_rx = 0
        self._timeCreated = time.time()
        self._connected = False

    def send(self):
        # Request is negligible, ignore it
        time.sleep(2 * self._latency_ms / 1000)  # Simulate the latency

        pass

    def receive(self, kbytes_total):
        time.sleep(2 * self._latency_ms / 1000)  # Simulate the latency
        kbytes_sent = 0
        data = []
        kb_per_100_msec = self._bandwidth_kbps / 10
        while kbytes_sent < kbytes_total:
            # Simulate 100 msec round trips
            kbytes_sent += kb_per_100_msec
            data.append(memory_chunk(kb_per_100_msec))
            time.sleep(100 / 1000)  # sleep 100 msec
            # Use a real data chunk to simulate a real object!

        self._kbytes_rx += kbytes_sent
        assert len(data) >= kbytes_total, f'BUG! {len(data)} {kbytes_total}'
        return data

    @property
    def kbytes_received(self):
        return self._kbytes_rx
