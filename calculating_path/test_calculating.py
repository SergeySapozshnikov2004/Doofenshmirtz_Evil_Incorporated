import unittest
from unittest.mock import patch, MagicMock
from calculating import Calculating_path, app, map
import numpy as np
import json

class TestCalculatingPath(unittest.TestCase):
    def setUp(self):
        # Сброс глобальных переменных перед каждым тестом
        global a_1, a_2, a_3, a_4
        a_1 = a_2 = a_3 = a_4 = 50
        
        # Тестовые координаты
        self.coordinates = {
            "x_start": 0,
            "y_start": 0,
            "x_end": 2,
            "y_end": 2
        }
        
        # Создаем тестовую карту для некоторых тестов
        self.test_map = np.array([
            [0, 0, 0],
            [0, 1, 0],
            [0, 0, 0]
        ])
    
    def test_get_direction_right_down(self):
        """Тестирование определения направления вправо-вниз"""
        coords = {"x_start": 0, "y_start": 0, "x_end": 1, "y_end": 1}
        calc = Calculating_path(coords)
        self.assertEqual(calc.get_direction(), 0)
    
    def test_get_direction_right_up(self):
        """Тестирование определения направления вправо-вверх"""
        coords = {"x_start": 0, "y_start": 1, "x_end": 1, "y_end": 0}
        calc = Calculating_path(coords)
        self.assertEqual(calc.get_direction(), 1)
    
    def test_get_direction_left_up(self):
        """Тестирование определения направления влево-вверх"""
        coords = {"x_start": 1, "y_start": 1, "x_end": 0, "y_end": 0}
        calc = Calculating_path(coords)
        self.assertEqual(calc.get_direction(), 2)
    
    def test_get_direction_left_down(self):
        """Тестирование определения направления влево-вниз"""
        coords = {"x_start": 1, "y_start": 0, "x_end": 0, "y_end": 1}
        calc = Calculating_path(coords)
        self.assertEqual(calc.get_direction(), 3)
    
    def test_calculating_direction_simple_path(self):
        """Тестирование расчета простого пути без препятствий"""
        # Временно заменяем глобальную карту на тестовую
        global map
        original_map = map
        map = self.test_map
        
        try:
            coords = {"x_start": 0, "y_start": 0, "x_end": 2, "y_end": 2}
            calc = Calculating_path(coords)
            path = calc.calculating_direction()
            
            # Ожидаемый путь: вправо (2), вправо (2), вниз (0), вниз (0)
            # или вниз (0), вниз (0), вправо (2), вправо (2)
            # или комбинация этих направлений
            self.assertTrue(len(path) >= 2)  # Минимальная длина пути
            self.assertTrue(all(d in (0, 2) for d in path))  # Только вниз или вправо
        finally:
            # Восстанавливаем оригинальную карту
            map = original_map
    
    def test_calculating_direction_with_obstacle(self):
        """Тестирование обхода препятствия"""
        # Временно заменяем глобальную карту на тестовую
        global map
        original_map = map
        map = self.test_map
        
        try:
            coords = {"x_start": 0, "y_start": 0, "x_end": 2, "y_end": 0}
            calc = Calculating_path(coords)
            path = calc.calculating_direction()
            
            # Ожидаемый путь: вниз (0), вправо (2), вправо (2), вверх (1)
            # или другой вариант обхода препятствия
            self.assertTrue(len(path) > 2)  # Должен быть обход
            self.assertTrue(1 in path or 3 in path)  # Должно быть движение вверх или влево
        finally:
            # Восстанавливаем оригинальную карту
            map = original_map
    
    @patch('calculating.requests.post')
    def test_send_path_success(self, mock_post):
        """Тестирование успешной отправки пути"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = '{"status": "ok"}'
        mock_post.return_value = mock_response
        
        calc = Calculating_path(self.coordinates)
        calc.route = [0, 1, 2, 3]  # Тестовый путь
        
        with app.test_request_context():
            response = calc.send_path({'X': 0, 'Y': 0})
            response_data = json.loads(response.get_data(as_text=True))
            self.assertEqual(response_data, {"status": "success"})
            mock_post.assert_called_once()
    
    @patch('calculating.requests.post')
    def test_send_path_failure(self, mock_post):
        """Тестирование неудачной отправки пути"""
        mock_post.side_effect = requests.exceptions.RequestException("Error")
        
        calc = Calculating_path(self.coordinates)
        calc.route = [0, 1, 2, 3]  # Тестовый путь
        
        with app.test_request_context():
            response = calc.send_path({'X': 0, 'Y': 0})
            response_data = json.loads(response.get_data(as_text=True))
            self.assertEqual(response_data, {"status": "error"})

class TestAppRoutes(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.valid_data = {
            "x_start": 0,
            "y_start": 0,
            "x_end": 2,
            "y_end": 2
        }
    
    @patch('calculating.Calculating_path')
    def test_receive_coordinates_success(self, mock_calc):
        """Тестирование успешного получения координат"""
        mock_instance = mock_calc.return_value
        mock_instance.calculating_direction.return_value = [0, 1, 2]
        mock_instance.run.return_value = None
        
        response = self.app.post(
            '/calc',
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response_data["status"], "success")
    
    def test_receive_coordinates_invalid_json(self):
        """Тестирование невалидного JSON"""
        response = self.app.post(
            '/calc',
            data="invalid json",
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_receive_coordinates_missing_fields(self):
        """Тестирование отсутствия обязательных полей"""
        invalid_data = {
            "x_start": 0,
            "y_start": 0
            # Нет x_end и y_end
        }
        response = self.app.post(
            '/calc',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()

'''
TestCalculatingPath - тестирует класс Calculating_path:

test_get_direction_* - проверяют корректность определения направления движения

test_calculating_direction_simple_path - тестирует расчет пути без препятствий

test_calculating_direction_with_obstacle - проверяет обход препятствий

test_send_path_* - тестируют отправку маршрута на сервер

TestAppRoutes - тестирует Flask-роуты:

test_receive_coordinates_success - проверяет успешную обработку валидных координат

test_receive_coordinates_invalid_json - тестирует обработку невалидного JSON

test_receive_coordinates_missing_fields - проверяет обработку запроса с отсутствующими полями
'''
