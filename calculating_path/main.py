import numpy as np
from time import sleep
import requests
import os


import logging

logging.basicConfig(level=logging.INFO)  # Или logging.DEBUG

logging.info("Сообщение")
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Service Configuration
SERVICE_NAME = "calculating_path"
NEXT_SERVICE_URL = "http://autopilot:8002/report"
PORT = int(os.environ.get("PORT", 8001))


map = np.array(
[ #X 0  1  2  3  4  5  6  7  8  9    Y
    [1, 1, 0, 0, 1, 0, 0, 0, 0, 0],# 0
    [1, 1, 0, 1, 1, 0, 1, 0, 1, 0],# 1
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],# 2
    [1, 1, 1, 0, 1, 0, 0, 0, 1, 0],# 3
    [0, 1, 0, 0, 1, 1, 0, 0, 0, 0],# 4
    [0, 0, 0, 0, 1, 1, 0, 0, 1, 0],# 5
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0],# 6 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],# 7
    [1, 0, 0, 0, 0, 0, 1, 1, 1, 0],# 8
    [1, 0, 1, 0, 1, 0, 0, 1, 1, 1] # 9
]
)

# # TEST
# map = np.array(
# [ #X 0  1  2  3  4    Y
#     [0, 0, 0, 0, 0],# 0
#     [0, 0, 1, 0, 0],# 1
#     [1, 0, 0, 0, 0],# 2
#     [0, 0, 0, 0, 1],# 3
#     [0, 0, 0, 0, 0],# 4
# ]
# )

a_1 = 50
a_2 = 50
a_3 = 50
a_4 = 50

# route = list()

class Calculating_path():
    coord_start = dict()
    coord_end = dict()
    route = list()


    def __init__(self, coordinates):
        self.coord_start["x"] = coordinates["x_start"]
        self.coord_start["y"] = coordinates["y_start"]
        self.coord_end["x"] = coordinates["x_end"]
        self.coord_end["y"] = coordinates["y_end"]

    def get_direction(self):
        x_start = self.coord_start["x"]
        y_start = self.coord_start["y"]
        x_end = self.coord_end["x"]
        y_end = self.coord_end["y"]
        delta_x = x_start - x_end
        delta_y = y_start - y_end
        if delta_x < 0 and delta_y < 0:
            return 0
            
        if delta_x < 0 and delta_y > 0:
            return 1 

        if delta_x > 0 and delta_y > 0:
            return 2

        if delta_x > 0 and delta_y < 0:
            return 3

        if delta_x < 0 and delta_y == 0:
            return 4 #ВПРАВО

        if delta_x > 0 and delta_y == 0:
            return 5 #ВЛЕВО

        if delta_x == 0 and delta_y > 0:
            return 6 #ВВЕРХ

        if delta_x == 0 and delta_y < 0:
            return 7 #ВНИЗ
    def calculating_direction(self):
        global a_1
        global a_2
        global a_3
        global a_4
        if self.coord_start != self.coord_end:
            x = self.coord_start["x"]
            y = self.coord_start["y"]
            print("x: ", x, " y: ", y)
            # print(self.get_direction())
            if self.get_direction() == 0 or self.get_direction() == 3 or self.get_direction() == 7: 
                if y != map.shape[1] - 1:
                    if a_1 != 0:
                        a_1 -= 1
                        coordinates = {"x_start": x, "y_start": y+1, "x_end": self.coord_end["x"], "y_end": self.coord_end["y"]}
                        if map[y+1][x] == 0: #ФУНКИЦЯ ВНИЗ
                            new_calc = Calculating_path(coordinates)
                            new_calc.calculating_direction()
                            self.route.append(0)
                            # print("x: " ,self.coord_start["x"], " ", "y: ", self.coord_start["y"])
                            return
                        else: 
                            pass
            if self.get_direction() == 1 or self.get_direction() == 2 or self.get_direction() == 6:
                if y != 0:
                    if a_3 != 0:
                        a_3 -= 1
                        coordinates = {"x_start": x, "y_start": y-1, "x_end": self.coord_end["x"], "y_end": self.coord_end["y"]}
                        if map[y-1][x] == 0 and x: #ФУНКИЦЯ ВВЕРХ
                            new_calc = Calculating_path(coordinates)
                            new_calc.calculating_direction()
                            self.route.append(1)
                            # print("x: ", self.coord_start["x"], " ", "y: ", self.coord_start["y"])
                            return
                        else:
                            pass                            
            if self.get_direction() == 0 or self.get_direction() == 1 or self.get_direction() == 4 or self.get_direction() == 6 or self.get_direction() == 7:
                if x != map.shape[0] - 1:
                    if a_2 != 0:
                        a_2 -= 1
                        coordinates = {"x_start": x+1, "y_start": y, "x_end": self.coord_end["x"], "y_end": self.coord_end["y"]}
                        if map[y][x+1] == 0: #ФУНКИЦЯ ВПРАВО
                            new_calc = Calculating_path(coordinates)
                            new_calc.calculating_direction()
                            self.route.append(2)
                            # print("x: " ,self.coord_start["x"], " ", "y: ", self.coord_start["y"])
                            return
                        else:
                            pass
            if self.get_direction() == 2 or self.get_direction() == 3 or self.get_direction() == 5 or self.get_direction() == 6 or self.get_direction() == 7:
                if x != 0:
                    if a_4 != 0:
                        a_4 -= 1
                        coordinates = {"x_start": x-1, "y_start": y, "x_end": self.coord_end["x"], "y_end": self.coord_end["y"]}
                        if map[y][x-1] == 0: #ФУНКИЦЯ ВЛЕВО
                            new_calc = Calculating_path(coordinates)
                            new_calc.calculating_direction()
                            self.route.append(3)
                            # print("x: ", self.coord_start["x"], " ", "y: ", self.coord_start["y"])
                            return
                        else:
                            pass     
        else:
            print("Конечная точка x: " ,self.coord_start["x"], " ", "y: ", self.coord_start["y"])
            list_1 = self.route
            return list_1
        return self.route

    def print_start(self):
        print(self.coord_const["x"], self.coord_const["y"])
    
    def check_status():
        return

    def send_path(self, coordinates):
        try:
            # {"operation": {"priority": 3, "type": "burn"}, "mode": "Driving", "input_status": {"motor_system_status": True, "jet_system_status": True, "photo_sensor_status": True, "fast_reaction_system_status": True, "car_status": True}, "coordinates": {'X': 3, 'Y' : 6}, "direction": {"current_direction": "up", "step" : 2}}
            data_to_send = {'coordinates': coordinates, 'direction': self.route}
            logging.info(f"Sending to {NEXT_SERVICE_URL} with {data_to_send}")  # Логируем данные перед отправкой
            response = requests.post(NEXT_SERVICE_URL, json=data_to_send)
            response.raise_for_status()
            logging.info(f"{SERVICE_NAME} sent data to {NEXT_SERVICE_URL}. Response: {response.text}")
            success_msg = {"status": "success"}
            self.route.clear()    
            return jsonify(success_msg)
            
        except requests.exceptions.RequestException as e:
            print(f"Error sending message: {e}")
            success_msg = {"status": "error"}
            return jsonify(success_msg)

    def run(self, list, coordinates):
        self.send_path(coordinates=coordinates)


# coordinates_1 = {"x_start": 0, "y_start": 7, "x_end": 9, "y_end": 0}
# coordinates_2 = {"x_start": 9, "y_start": 0, "x_end": 0, "y_end": 7}
# coordinates_3 = {"x_start": 9, "y_start": 6, "x_end": 0, "y_end": 2}
# coordinates_4 = {"x_start": 0, "y_start": 2, "x_end": 9, "y_end": 6}


@app.route('/calc', methods=['POST'])
def receive_coordinates():
    try:
        # sleep(1)
        print("Calc_start")
        # sleep(1)
        data = request.get_json()
        coordinates = {"x_start": data["x_start"], "y_start": data["y_start"], "x_end": data["x_end"], "y_end": data["y_end"]}
        coord_start = {"X": data["x_start"], "Y": data["y_start"]}
        # data = {"coordinates": {"x_start": 0, "y_start": 7, "x_end": 9, "y_end": 0}}
        test_calc = Calculating_path(coordinates=coordinates)
        # sleep(2 )
        # breakpoint()
        list_1 = test_calc.calculating_direction()
        test_calc.run(list=list_1, coordinates=coord_start)
        return jsonify({"status": "success", "message": "Coordinates processed"}), 200 # Возвращаем jsonify()
    except Exception as e:
        print(f"Error processing message: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


# sleep(1)
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8001)


#     while True:
#     print("autopilot is working")
#     sleep(2)

# print("Начался расчёт пути!")
# data = {"coordinates": {"x_start": 0, "y_start": 7, "x_end": 9, "y_end": 0}}
# test_calc = Calculating_path(data["coordinates"])
# test_calc.print_start()
# test_calc.calculating_direction()
# print("Расчёт пути окончен!")
# test_calc.print_start()
# print(route)