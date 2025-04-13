from flask import Flask, request, jsonify
import requests
from time import sleep
from time import time
import json
import os


import logging

logging.basicConfig(level=logging.INFO)  # Или logging.DEBUG

logging.info("Сообщение")
app = Flask(__name__)

count = 1
# Service Configuration
SERVICE_NAME = "planning_system"
NEXT_SERVICE_URL = "http://calculating_path:8001/calc"
INITIAL_DATA = {"x_start": 0, "y_start": 7, "x_end": 9, "y_end": 0}
PORT = int(os.environ.get("PORT", 8000))

# url = 'http://planning_system:8000/task'
# data = {'coordinates': {"x_start": 0, "y_start": 0, "x_end": 5, "y_end": 6}, "operation": {"priority" : 3, "type": "terror"}}
    
class Mission():
    coordinates = dict()
    operation = dict()

    def __init__(self, coordinates, operation):
        self.coordinates = coordinates
        self.operation = operation

class Planning_system():
    mission = Mission(coordinates=dict(), operation=dict())

    def __init__(self, mission):
        self.mission = mission

    def check_correct_coordinates(self):
        coordinates = self.mission.coordinates
        x_start = (coordinates["x_start"])
        y_start = (coordinates["y_start"])
        x_end = (coordinates["x_end"])
        y_end = (coordinates["y_end"])
        
        # Проверка на выход из массива
        if x_start > 10 or y_start > 10 or x_end > 10 or y_end > 10 or x_start < 0 or y_start < 0 or x_end < 0 or y_end < 0:
            if x_end != x_start and y_end != y_start:
                print("Координаты некорректны!")
                return False
        print("Координаты верны!")
        return True

    def send_data(self):
        try:
            coordinates = self.mission.coordinates
            data_to_send = {
                "x_start": coordinates["x_start"],
                "y_start": coordinates["y_start"],
                "x_end": coordinates["x_end"],
                "y_end": coordinates["y_end"]
            }
            logging.info(f"Sending to {NEXT_SERVICE_URL} with {data_to_send}")  # Логируем данные перед отправкой
            response = requests.post(NEXT_SERVICE_URL, json=data_to_send)
            response.raise_for_status()
            logging.info(f"{SERVICE_NAME} sent data to {NEXT_SERVICE_URL}. Response: {response.text}")

            success_msg = {"status": "success"}
            return jsonify(success_msg)
        except requests.exceptions.RequestException as e:
            print(f"Error sending {e}")
            success_msg = {"status": "error"}
            return jsonify(success_msg)
    
    def run(self):
        self.check_correct_coordinates()
        # sleep(2)
        self.send_data()



@app.route('/task', methods=['POST'])
def receive_data():
    try:
        # sleep(1)
        data = request.get_json()
        print("plan work")
        # breakpoint()
        # data = {'coordinates': {"x_start": 0, "y_start": 0, "x_end": 5, "y_end": 6}, "operation": {"priority" : 3, "type": "terror"}}
        mission = Mission(coordinates=data["coordinates"], operation=None)
        plan = Planning_system(mission)
        plan.run()
        # Дальше работаем с 'data' как со словарём Python
        processed_data = {"coordinates": data["coordinates"], "operation": data["operation"] }
        # sleep(4)
        return jsonify({"status": "success", "processed": processed_data})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500




if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=8000)
# data = {"coordinates": {"x_start": 9, "y_start": 6, "x_end": 0, "y_end": 2}, "operation": {"priority" : 3, "type": "terror"}}
# mission = Mission(coordinates=data["coordinates"], operation=None)
# plan = Planning_system(mission)
# plan.run()