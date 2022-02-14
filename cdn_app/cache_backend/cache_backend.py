# -*- coding: utf-8 -*-

import asyncio
import json
import math
import os
import sys
import time
import uuid
import threading
import logging
from collections import namedtuple
from collections import ChainMap
from contextlib import contextmanager

import fake_connection
from cpu_load_generator import load_single_core
from flask import Flask, request
from flask_cors import CORS

# Hack to alter sys path, so we will run from microservices package
# This hack will require us to import with absolute path from everywhere in this module
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(APP_ROOT))

app = Flask(__name__)
CORS(app)

latecy = os.getenv('BE_LATENCY_MS', 100)
bw = os.getenv('BE_BW_KBPS', 500 * 1024)  # 500 mbps
connection = fake_connection.FakeConnection(latency_ms=latecy, bandwidth_kbps=bw)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
logger.addHandler(console)


def memory_chunk(size_in_kb):
    l = []
    logger.info(size_in_kb)
    logger.info(type(size_in_kb))
    for i in range(0, int(size_in_kb)):
        l.append("*" * 1024)  # 1KB
    return l


async def generate_memory_load(params, transaction_id):
    if params is None:
        return {'mem_load': 0}
    logger.debug(f'{transaction_id} Generating memory load with params {params}')
    duration_seconds = params.get("duration_seconds", 0.1)  # def 100ms
    kb_count = params.get("kb_count", 64)  # def 64KB
    mem_chunk = memory_chunk(kb_count)
    await asyncio.sleep(duration_seconds)

    #def _del_obj(obj, transaction_id):
    #    logger.debug(f'{transaction_id} deleting object')
    #    del obj

    # TODO take care of cleanup if needed
    # loop.call_later(duration_seconds, _del_obj, mem_chunk, transaction_id)

    if params is None:
        return {'mem_load': 0}


async def generate_cpu_load(params, transaction_id):
    if params is None:
        return {'cpu_load': 0}
    logger.debug(f'{transaction_id} Generating cpu load with params {params}')

    duration_seconds = params.get("duration_seconds", 0.1)  # def 100ms
    cpu_load = params.get("load", 0.1)  # def 10%
    core_num = params.get("core_num", 0)  # def 0
    load_single_core(core_num=core_num,
                     duration_s=duration_seconds,
                     target_load=cpu_load)
    await asyncio.sleep(duration_seconds)
    return ""


current_objects = []
CacheObj = namedtuple('CacheObj', ['data', 'size_mb', 'ttl_ts', 'uuid'])


@contextmanager
def time_ctx(op):
    start_time = time.monotonic()
    yield
    logger.info('{} took {}'.format(op, time.monotonic() - start_time))


def generate_network_load(params, transaction_id):
    global current_objects
    logger.debug(f'{transaction_id} Generating network load with params {params}')

    if params is None:
        return {'network_load': 0}

    object_size_mb = math.ceil(params.get("object_size_mb", 100))  # def 100 mb
    ttl_sec = math.ceil(params.get('object_ttl_sec', 120))
    obj_uuid = params.get('object_uuid', 120)
    with time_ctx('connection.send'):
        connection.send()  # Simulate sending the request
    with time_ctx('connection.receive'):
        obj = connection.receive(kbytes_total=object_size_mb * 1024)

    current_objects.append(CacheObj(data=obj, size_mb=object_size_mb, ttl_ts=time.monotonic() + ttl_sec, uuid=obj_uuid))

    return {'network_load': object_size_mb,
            'total_network_load': connection.kbytes_received}


def _cleanup_thread():
    logger.info(f'Starting cleanup thread')
    global current_objects
    while True:
        cleaned_objs = [obj.uuid for obj in current_objects if obj.ttl_ts <= time.monotonic()]
        current_objects = [obj for obj in current_objects if obj.ttl_ts > time.monotonic()]
        if cleaned_objs:
            logger.info(f'Cleaned {cleaned_objs}')
        time.sleep(2)


@app.route('/health', methods=['GET'])
def health():
    return 'HELLO from cache_backend!'


@app.route('/stats', methods=['GET'])
def get_stats():
    received_kbytes = connection.kbytes_received
    return json.dumps({"network_kbytes": received_kbytes})


@app.route('/load', methods=['POST'])
def load():
    transaction_id = uuid.uuid4()
    logger.info(f"{transaction_id} running load with options {request.json}")
    response = generate_network_load(request.json.get('network_params', None), transaction_id)
    return json.dumps(response)


if __name__ == '__main__':
    threading.Thread(target=_cleanup_thread).start()
    # threaded=True is a debugging feature, use WSGI for production!
    app.run(host='0.0.0.0', port='8081', threaded=False)
