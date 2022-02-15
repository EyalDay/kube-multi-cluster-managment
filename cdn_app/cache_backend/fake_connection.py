import math
import time
#import utils
import random
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
logger.addHandler(console)

def memory_chunk(size_in_kb):
    return random.getrandbits(size_in_kb * 1024)

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
        kbytes_received = 0
        data = []
        kb_per_100_msec = int(math.ceil(self._bandwidth_kbps / 10))
        while kbytes_received < kbytes_total:
            # Simulate 100 msec round trips
            kbytes_received += kb_per_100_msec
            # Use a real data chunk to simulate a real object
            data.append(memory_chunk(kb_per_100_msec))
            #logger.info('sleep')
            time.sleep(100 / 1000)  # sleep 100 msec

        self._kbytes_rx += kbytes_received
        return data

    @property
    def kbytes_received(self):
        return self._kbytes_rx
