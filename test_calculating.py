import pytest
import json
from calculating import *

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_receive_coordinates(client):
    # Тестовые координаты
    test_data = {
        "x_start": 0,
        "y_start": 7,
        "x_end": 9,
        "y_end": 0
    }
    
    # Отправка POST-запроса
    response = client.post('/calc', data=json.dumps(test_data), content_type='application/json')
    
    # Проверка статуса ответа
    assert response.status_code == 200
    
    # Проверка содержимого ответа
    response_data = json.loads(response.data)
    assert response_data["status"] == "success"
    assert response_data["message"] == "Coordinates processed"

def test_invalid_coordinates(client):
    # Тестовые некорректные координаты
    test_data = {
        "x_start": 10,
        "y_start": 10,
        "x_end": 0,
        "y_end": 0
    }
    
    # Отправка POST-запроса
    response = client.post('/calc', data=json.dumps(test_data), content_type='application/json')
    
    # Проверка статуса ответа
    assert response.status_code == 400
    
    # Проверка содержимого ответа на ошибку
    response_data = json.loads(response.data)
    assert response_data["status"] == "error"

def test_calculating_direction(client):
    # Тестовые координаты для проверки направления
    test_data = {
        "x_start": 0,
        "y_start": 0,
        "x_end": 4,
        "y_end": 4
    }
    
    # Отправка POST-запроса
    response = client.post('/calc', data=json.dumps(test_data), content_type='application/json')
    
    # Проверка статуса ответа
    assert response.status_code == 200
    
    # Проверка содержимого ответа
    response_data = json.loads(response.data)
    assert response_data["status"] == "success"

if __name__ == '__main__':
    pytest.main()
