from flask import Flask, request, jsonify
import json
import os
app = Flask(__name__)
import requests
import time
# Service Configuration
SERVICE_NAME = "autopilot"
NEXT_SERVICE_URL = "http://planning_system:8000/task"
PORT = int(os.environ.get("PORT", 8002))



import logging

logging.basicConfig(level=logging.INFO)  # Или logging.DEBUG

class Status():        
    motor_system_status = True
    jet_system_status = True
    photo_sensor_status = True
    fast_reaction_system_status = True
    car_mode = "Sleep_mode"

    def __init__(self, input_status, mode):
        self.motor_system_status = input_status["motor_system_status"]
        self.jet_system_status = input_status["jet_system_status"]
        self.photo_sensor_status = input_status["photo_sensor_status"]
        self.car_status = input_status["car_status"]
        self.fast_reaction_system_status = input_status["fast_reaction_system_status"]
        self.car_mode = mode

    def status_correct (self):
        if self.car_status and self.fast_reaction_system_status and self.jet_system_status and self.motor_system_status and self.photo_sensor_status:
            return True
        else:
            return False
    def check_incorrect_statuses(self):
        ##Проверяет значения атрибутов класса и печатает сообщение, если какой-либо из них False.
    
        if not self.motor_system_status:
            print("ходовая часть сломалась!", end='\n')
        if not self.jet_system_status:
            print("реактивный двигатель выведен из строя!", end='\n')
        if not self.photo_sensor_status:
            print("Фото-чувствительный датчики не отзываются!", end='\n')
        if not self.fast_reaction_system_status:
            print("Система бысрого реагирования ответила сбоем!", end='\n')

    def check_mode(self):
        if self.car_mode == "Driving":
            return True
        else:
            return False

    def get_mode(self):
        return self.car_mode

class Autopilot():
    coordinates = {'X': 0, 'Y' : 0}
    passenger_status = None
    direction = list()

    def __init__(self, coordinates, direction, status):
        self.coordinates = coordinates
        self.direction = direction
        self.passenger_status = status

    def drive(self):
        print("Движение началось")
        for i in range(len(self.direction)):
            self.generate_status()
            if self.direction[i] == 1:
                self.coordinates['Y'] += 1

            if self.direction[i] == 0:
                self.coordinates['Y'] -= 1

            if self.direction[i] == 2:
                self.coordinates['X'] += 1

            if self.direction[i] == 3:
                self.coordinates['X'] -= 1
        print("Движение окончено")

    def generate_status(self):
        print("Координаты: (", self.coordinates['X'],", ", self.coordinates['Y'], ") ")
        print()
        # mode = self.passenger_status.get_mode()
        # print(f"Текущий режим работы: {mode}.")
        # if self.passenger_status.status_correct():
        #     print("Все системы в норме!", end='\n')
        #     print()
        # else:
        #     self.passenger_status.check_incorrect_statuses()
        #     print()

    def run(self):
        # if self.passenger_status.check_mode():
        self.drive()
        self.generate_status()
        # else:
        #     # mode = self.passenger_status.get_mode()
        #     print("Машина не может выполнить задачу. Она введена в режим: !")
    
    
    def send_command(self):
        # try:
            # data_to_send = {"status": "win!"}
            # logging.info(f"Sending to {NEXT_SERVICE_URL} with {data_to_send}")  # Логируем данные перед отправкой
            # response = requests.post(NEXT_SERVICE_URL, json=data_to_send)
            # response.raise_for_status()
            # logging.info(f"{SERVICE_NAME} sent data to {NEXT_SERVICE_URL}. Response: {response.text}")

            success_msg = {"status": "success"}
            return jsonify(success_msg)
        # except requests.exceptions.RequestException as e:
        #     print(f"Error sending message: {e}")
        #     success_msg = {"status": "error"}
        #     return jsonify(success_msg)

# direction_1 = {"current_direction": "up", "step" : 2}
# direction_2 = {"current_direction": "right", "step" : 3}
# direction_3 = {"current_direction": "down", "step" : 2}
# direction_4 = {"current_direction": "left", "step" : 1}
# status = {"motor_system_status": True,
# "jet_system_status": True,
# "photo_sensor_status": True,
# "car_status": True,
# "fast_reaction_system_status": True}
# mode = "Driving"
# coord = {"X": 10, "Y": 10}
# auto = Autopilot(coord, direction_1, Status(status, mode))



@app.route('/report', methods=['POST'])
def receive_operation():
    try:
        # time.sleep(1)
        data = request.get_json()
        # time.sleep(4)
        # status = Status(input_status=data["input_status"], mode=data["mode"])
        auto = Autopilot(coordinates=data["coordinates"], direction=data["direction"], status=None)
        auto.run()
        # breakpoint()
        auto.send_command()
        return jsonify({"status": "success", "message": "Autopilot good"}), 200 # Возвращаем jsonify()
    except Exception as e:
        print(f"Error processing message: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

# time.sleep(3)
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8002)
# while True:
#     print("autopilot is working")
#     sleep(2)
# data = {"coordinates": {'X': 0, 'Y' : 0}, "direction": [2, 2, 2, 2, 1, 1, 2, 2, 1, 1, 2, 1, 2, 1, 1, 2]}
# auto = Autopilot(coordinates=data["coordinates"], direction=data["direction"], status=None)
# auto.run()