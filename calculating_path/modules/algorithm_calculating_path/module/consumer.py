import os
import json
import threading

from uuid import uuid4
from confluent_kafka import Consumer, OFFSET_BEGINNING
import requests

from .producer import proceed_to_deliver

MODULE_NAME: str = os.getenv("MODULE_NAME")
AUTOPILOT_URL = "/autopilot"

def post_path(path):
    requests.post(f'{AUTOPILOT_URL}/post_path', json=path)
    return None

def send_to_calculating_the_optimal_path(id, details, coordinates):
    details["deliver_to"] = "calculating_the_optimal_path"
    proceed_to_deliver(id, details, coordinates)


def handle_event(id, details_str):
    """ Обработчик входящих в модуль задач. """
    details = json.loads(details_str)
    if details("operation") == "get_coord":
        print("координаты отправлены")
        send_to_calculating_the_optimal_path(id, details, details["coordinates"]) 
    elif details("operation") == "get_path":
        print("Маршрут отправлен")
        post_path(path=details("path"))

    return None

def consumer_job(args, config):
    consumer = Consumer(config)

    def reset_offset(verifier_consumer, partitions):
        if not args.reset:
            return

        for p in partitions:
            p.offset = OFFSET_BEGINNING
        verifier_consumer.assign(partitions)

    topic = MODULE_NAME
    consumer.subscribe([topic], on_assign=reset_offset)

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                pass
            elif msg.error():
                print(f"[error] {msg.error()}")
            else:
                try:
                    id = msg.key().decode('utf-8')
                    details_str = msg.value().decode('utf-8')
                    handle_event(id, details_str)
                except Exception as e:
                    print(f"[error] Malformed event received from " \
                          f"topic {topic}: {msg.value()}. {e}")
    except KeyboardInterrupt:
        pass

    finally:
        consumer.close()

def start_consumer(args, config, response_queue):
    global _response_queue
    _response_queue = response_queue
    print(f'{MODULE_NAME}_consumer started')

    threading.Thread(target=lambda: consumer_job(args, config)).start()