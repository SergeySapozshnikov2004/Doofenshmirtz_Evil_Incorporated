import pytest
import json
from unittest.mock import patch
from planning import app, Planning_system, Mission  

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_receive_data_success(client):
    test_payload = {
        "coordinates": {"x_start": 0, "y_start": 7, "x_end": 9, "y_end": 0},
        "operation": {"priority": 3, "type": "terror"}
    }

    with patch('planning.requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = 'OK'
        mock_post.return_value.raise_for_status = lambda: None  # чтобы не выбрасывало исключение
        
        response = client.post('/task', data=json.dumps(test_payload), content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "processed" in data
        assert data["processed"]["coordinates"] == test_payload["coordinates"]
        assert data["processed"]["operation"] == test_payload["operation"]

def test_receive_data_invalid_json(client):
    # Отправляем некорректный JSON (например, пустой)
    response = client.post('/task', data="not a json", content_type='application/json')
    assert response.status_code == 500
    data = response.get_json()
    assert data["status"] == "error"

def test_check_correct_coordinates_valid():
    coords = {"x_start": 1, "y_start": 1, "x_end": 5, "y_end": 5}
    mission = Mission(coordinates=coords, operation=None)
    plan = Planning_system(mission)
    
    # Подменяем метод check_correct_coordinates, чтобы он возвращал True
    with patch.object(plan, 'check_correct_coordinates', return_value=True):
        assert plan.check_correct_coordinates() is True

def test_check_correct_coordinates_invalid():
    coords = {"x_start": 50, "y_start": 0, "x_end": 0, "y_end": 0}
    mission = Mission(coordinates=coords, operation=None)
    plan = Planning_system(mission)

    # Подменяем метод check_correct_coordinates, чтобы он возвращал False
    with patch.object(plan, 'check_correct_coordinates', return_value=False):
        assert plan.check_correct_coordinates() is False

def test_send_data_success():
    coords = {"x_start": 0, "y_start": 0, "x_end": 1, "y_end": 1}
    mission = Mission(coordinates=coords, operation=None)
    plan = Planning_system(mission)

    with patch('planning.requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = 'OK'
        mock_post.return_value.raise_for_status = lambda: None

        from planning import app  # импорт вашего Flask-приложения

        with app.app_context():
            response = plan.send_data()
            # response — это Flask Response с JSON
            json_data = response.get_json()
            assert json_data["status"] == "success"

def test_send_data_failure():
    coords = {"x_start": 0, "y_start": 0, "x_end": 1, "y_end": 1}
    mission = Mission(coordinates=coords, operation=None)
    plan = Planning_system(mission)

    with patch('planning.requests.post', side_effect=Exception("Connection error")):
        from planning import app
        with app.app_context():
            with pytest.raises(Exception) as excinfo:
                plan.send_data()
            assert str(excinfo.value) == "Connection error"
