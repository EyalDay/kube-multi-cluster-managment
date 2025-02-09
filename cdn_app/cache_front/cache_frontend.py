# -*- coding: utf-8 -*-
import json
import logging
import os
import sys
import threading
import time
import uuid
from collections import namedtuple
import fake_connection
import requests
from flask import Flask, request
from flask_cors import CORS

# Hack to alter sys path, so we will run from microservices package
# This hack will require us to import with absolute path from everywhere in this module
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(APP_ROOT))

app = Flask(__name__)
CORS(app)

lock = threading.Lock()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
logger.addHandler(console)

latecy = int(os.getenv('BE_LATENCY_MS', 20))
bw = int(os.getenv('BE_BW_KBPS', 500 * 1024))  # 500 mbps
connection = fake_connection.FakeConnection(latency_ms=latecy, bandwidth_kbps=bw)


@app.route('/health', methods=['GET'])
def health():
    return 'OK'


@app.route('/stats', methods=['GET'])
def get_stats():
    received_kbytes = connection.kbytes_received
    return json.dumps({"network_kbytes": received_kbytes})


current_objects = {}
cache_hits = 0
cache_miss = 0

CacheObj = namedtuple('CacheObj', ['data', 'size_mb', 'ttl_ts', 'uuid'])


@app.route('/get_object', methods=['GET'])
def get_object():
    transaction_id = uuid.uuid4()
    _clean_objects(transaction_id)
    global cache_hits
    global cache_miss
    global current_objects

    logger.info(f"{transaction_id} running load with options {request.json}")

    obj_hash = request.args.get("obj_hash")
    obj_size_mb = int(request.args.get("obj_size_mb"))
    obj_ttl_sec = int(request.args.get("obj_ttl_sec"))
    logger.info(f'get_object called with {obj_hash} {obj_size_mb} {obj_ttl_sec}')
    with lock:
        if obj_hash in current_objects:
            cache_hits += 1
            logger.info(f'cache hit {cache_miss} {cache_hits}')

            return json.dumps({"cache_stats": {"hits": cache_hits, "miss": cache_miss}})
        cache_miss += 1
        logger.info(f'cache miss {cache_miss} {cache_hits}')
        be = os.getenv('CACHE_BACKEND_SERVICE_NAME', 'final-backend-service')
        be_port = int(os.getenv('CACHE_BACKEND_PORT', 8081))
        namespace = os.getenv('NAMESPACE_NAME', 'default')
        cluster= os.getenv('CLUSTER_NAME', 'networking-final')
        be_target = os.getenv('BE_TARGET', 'load')
        explicit_target = os.getenv('EXPLICIT_TARGET', 'http://34.134.171.50:8081/load')

        keep_object = bool(os.getenv('FRONTEND_KEEP_OBJ', False))
        obj = connection.receive(obj_size_mb * 1024) if keep_object else None
        current_objects[obj_hash] = CacheObj(ttl_ts=time.monotonic() + obj_ttl_sec,
                                             data=obj, uuid=obj_hash,
                                             size_mb=obj_size_mb)

    target = explicit_target or f"http://{be}.{namespace}.svc.{cluster}.local:{be_port}/{be_target}"
    try:
        json_data = {'network_params': {"object_size_mb": obj_size_mb, "object_ttl_sec": obj_ttl_sec}}
        logger.debug(f'Sending post request to {target} with {json.dumps(json_data)}')
        timeout = float(os.getenv('CACHE_BACKEND_TIMEOUT', 60))
        requests.post(target, data=None, json=json_data, timeout=float(timeout))
        logger.debug(f'DONE sending post request to {target} with {json.dumps(json_data)}')
    except Exception as e:
        logger.info(f'failed to issue post command to {target}: {e}')


    return json.dumps({"cache_stats": {"hits": cache_hits, "miss": cache_miss}})


def _clean_objects(transaction_id):
    global current_objects

    # Case 1 - clean old objects
    current_time = time.monotonic()
    with lock:
        pre = set(current_objects.keys())
        current_objects = {obj_hash: val for obj_hash, val in current_objects.items() if val.ttl_ts > current_time}
        diff = pre - set(current_objects.keys())

        if diff:
            logger.info(f'{transaction_id} Cleaned {len(diff)} objects: {diff} because their ttl passed')

    # case 2 - cache exceeded 30 gb
    max_size = int(os.getenv('MAX_CACHE_SIZE ', 30 * 1000))
    total_size = sum([obj.size_mb for obj in current_objects.values()])
    while total_size > max_size:
        logger.info(f'total size is now f{total_size}')
        pre = set(current_objects.keys())
        min_time = min([obj.ttl_ts for obj in current_objects.values()])
        current_objects = {obj_hash: val for obj_hash, val in current_objects.items() if val.ttl_ts != min_time}
        total_size = sum([obj.size_mb for obj in current_objects.values()])
        diff = pre - set(current_objects.keys())
        if diff:
            logger.info(f'{transaction_id} Cleaned {len(diff)} objects: {diff} because cache exceeded max size')


if __name__ == '__main__':
    # threaded=True is a debugging feature, use WSGI for production!
    # threading.Thread(target=_clean_objects).start()
    logger.info('Start on port 8082')
    app.run(host='0.0.0.0', port='8082', threaded=False)
