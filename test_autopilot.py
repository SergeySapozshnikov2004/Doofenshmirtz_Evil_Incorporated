import pytest
from autopilot import app, Status, Autopilot
from flask import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_status_correct_true():
    input_status = {
        "motor_system_status": True,
        "jet_system_status": True,
        "photo_sensor_status": True,
        "car_status": True,
        "fast_reaction_system_status": True
    }
    status = Status(input_status, "Driving")
    assert status.status_correct() is True

def test_status_correct_false():
    input_status = {
        "motor_system_status": False,
        "jet_system_status": True,
        "photo_sensor_status": True,
        "car_status": True,
        "fast_reaction_system_status": True
    }
    status = Status(input_status, "Driving")
    assert status.status_correct() is False

def test_check_mode():
    input_status = {
        "motor_system_status": True,
        "jet_system_status": True,
        "photo_sensor_status": True,
        "car_status": True,
        "fast_reaction_system_status": True
    }
    status = Status(input_status, "Driving")
    assert status.check_mode() is True
    status2 = Status(input_status, "Sleep_mode")
    assert status2.check_mode() is False

def test_autopilot_drive_and_coordinates():
    # Начальные координаты
    coords = {'X': 0, 'Y': 0}
    # Направления: 2 - вправо, 1 - вверх, 0 - вниз, 3 - влево
    direction = [2, 2, 1, 0, 3]
    autopilot = Autopilot(coords.copy(), direction, status=None)
    autopilot.drive()
    # После движения:
    # X: 0 + 1 + 1 + 0 + 0 - 1 = 1
    # Y: 0 + 0 + 0 + 1 - 1 + 0 = 0
    assert autopilot.coordinates['X'] == 1
    assert autopilot.coordinates['Y'] == 0

def test_receive_operation_success(client):
    data = {
        "coordinates": {'X': 0, 'Y': 0},
        "direction": [2, 2, 1, 0, 3]
    }
    response = client.post('/report', json=data)
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data['status'] == "success"
    assert json_data['message'] == "Autopilot good"

def test_receive_operation_bad_request(client):
    # Отправляем некорректный json (например, без координат)
    data = {
        "direction": [2, 2, 1, 0, 3]
    }
    response = client.post('/report', json=data)
    json_data = response.get_json()
    assert response.status_code == 400
    assert json_data['status'] == "error"
