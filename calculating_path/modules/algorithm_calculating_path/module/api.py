import os
import time
import json
import threading
import multiprocessing

from uuid import uuid4
from flask import Flask, request, jsonify, abort
from werkzeug.exceptions import HTTPException
import requests

# Константы
HOST: str = "0.0.0.0"
PORT: int = int(os.getenv("MODULE_PORT"))
MODULE_NAME: str = os.getenv("MODULE_NAME")
MAX_WAIT_TIME: int = 30
NEXT_SERVICE_URL = "http://communication_module_calc:6068/coordinates"
# Очереди задач и ответов
_requests_queue: multiprocessing.Queue = None
_response_queue: multiprocessing.Queue = None


app = Flask(__name__)

def wait_response():
    """ Ожидает завершение выполнения задачи. """
    start_time = time.time()
    while 1:
        if time.time() - start_time > MAX_WAIT_TIME:
            break

        try:
            response = _response_queue.get(timeout=MAX_WAIT_TIME)
        except Exception as e:
            print("[COM-MOBILE_DEBUG] timeout...", e)
            continue

        if not isinstance(response, dict):
            print("[COM-MOBILE_DEBUG] not a dict...")
            continue

        data = response.get('data')
        if response.get('deliver_to') != 'com-mobile' or not data:
            print("[COM-MOBILE_DEBUG] something strange...")
            continue

        print("[COM-MOBILE_DEBUG] response", response)
        return data

    print("[COM-MOBILE_DEBUG] OUT OF TIME...")

    return None

def send_to_control_system(details):
    if not details:
        abort(400)

    details["deliver_to"] = "calculating_the_optimanl_path"
    details["source"] = MODULE_NAME
    details["id"] = uuid4().__str__()

    details["deliver_to"] = "encryption_plan"
    details["source"] = MODULE_NAME
    details["id"] = uuid4().__str__()
    response = requests.post(NEXT_SERVICE_URL, json=details)
    response.raise_for_status()
    success_msg = {"status": "success"}
    return jsonify(success_msg)
    
def send_to_calculating_the_optimanl_path(details):
    if not details:
        abort(400)

    details["deliver_to"] = "calculating_the_optimanl_path"
    details["source"] = MODULE_NAME
    details["id"] = uuid4().__str__()

    try:
        _requests_queue.put(details)
        print(f"{MODULE_NAME} update event: {details}")
    except Exception as e:
        print("[RECEIVER_CAR_DEBUG] malformed request", e)
        abort(400)


# Обработчик ошибок
@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({
        "status": e.code,
        "name": e.name,
    }), e.code


def start_web(requests_queue, response_queue):
    global _requests_queue
    global _response_queue

    _requests_queue = requests_queue
    _response_queue = response_queue

    threading.Thread(target=lambda: app.run(
        host=HOST, port=PORT, debug=True, use_reloader=False
    )).start()