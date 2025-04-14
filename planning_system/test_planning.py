import unittest
from unittest.mock import patch, MagicMock
from planning import Mission, Planning_system, app
import json

class TestMission(unittest.TestCase):
    def setUp(self):
        self.coordinates = {
            "x_start": 0,
            "y_start": 0,
            "x_end": 5,
            "y_end": 5
        }
        self.operation = {
            "priority": 3,
            "type": "terror"
        }
    
    def test_mission_initialization(self):
        """Тестирование инициализации миссии"""
        mission = Mission(coordinates=self.coordinates, operation=self.operation)
        self.assertEqual(mission.coordinates, self.coordinates)
        self.assertEqual(mission.operation, self.operation)

class TestPlanningSystem(unittest.TestCase):
    def setUp(self):
        self.coordinates = {
            "x_start": 0,
            "y_start": 0,
            "x_end": 5,
            "y_end": 5
        }
        self.operation = {
            "priority": 3,
            "type": "terror"
        }
        self.mission = Mission(coordinates=self.coordinates, operation=self.operation)
        self.planning = Planning_system(self.mission)
    
    def test_check_correct_coordinates_valid(self):
        """Тестирование проверки корректных координат"""
        self.assertTrue(self.planning.check_correct_coordinates())
    
    def test_check_correct_coordinates_invalid(self):
        """Тестирование проверки некорректных координат"""
        invalid_coords = {
            "x_start": -1,
            "y_start": 0,
            "x_end": 11,
            "y_end": 5
        }
        invalid_mission = Mission(coordinates=invalid_coords, operation=self.operation)
        invalid_planning = Planning_system(invalid_mission)
        self.assertFalse(invalid_planning.check_correct_coordinates())
    
    @patch('planning.requests.post')
    def test_send_data_success(self, mock_post):
        """Тестирование успешной отправки данных"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = '{"status": "ok"}'
        mock_post.return_value = mock_response
        
        with app.test_request_context():
            response = self.planning.send_data()
            response_data = json.loads(response.get_data(as_text=True))
            self.assertEqual(response_data, {"status": "success"})
            mock_post.assert_called_once()
    
    @patch('planning.requests.post')
    def test_send_data_failure(self, mock_post):
        """Тестирование неудачной отправки данных"""
        mock_post.side_effect = requests.exceptions.RequestException("Error")
        
        with app.test_request_context():
            response = self.planning.send_data()
            response_data = json.loads(response.get_data(as_text=True))
            self.assertEqual(response_data, {"status": "error"})
    
    @patch.object(Planning_system, 'check_correct_coordinates')
    @patch.object(Planning_system, 'send_data')
    def test_run(self, mock_send, mock_check):
        """Тестирование основного метода run"""
        mock_check.return_value = True
        mock_send.return_value = jsonify({"status": "success"})
        
        self.planning.run()
        mock_check.assert_called_once()
        mock_send.assert_called_once()

class TestAppRoutes(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.valid_data = {
            "coordinates": {
                "x_start": 0,
                "y_start": 0,
                "x_end": 5,
                "y_end": 5
            },
            "operation": {
                "priority": 3,
                "type": "terror"
            }
        }
    
    @patch('planning.Planning_system')
    def test_receive_data_success(self, mock_planning):
        """Тестирование успешного получения данных"""
        mock_instance = mock_planning.return_value
        mock_instance.run.return_value = None
        
        response = self.app.post(
            '/task',
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response_data["status"], "success")
    
    def test_receive_data_invalid_json(self):
        """Тестирование невалидного JSON"""
        response = self.app.post(
            '/task',
            data="invalid json",
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 500)
    
    def test_receive_data_missing_fields(self):
        """Тестирование отсутствия обязательных полей"""
        invalid_data = {
            "coordinates": {
                "x_start": 0,
                "y_start": 0
                # Нет x_end и y_end
            },
            "operation": {
                "priority": 3,
                "type": "terror"
            }
        }
        response = self.app.post(
            '/task',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 500)

if __name__ == '__main__':
    unittest.main()

'''
TestMission - тестирует класс Mission:

Проверяет корректность инициализации объекта миссии

TestPlanningSystem - тестирует класс Planning_system:

test_check_correct_coordinates_* - проверяет валидацию координат

test_send_data_* - тестирует отправку данных на сервер

test_run - проверяет основной метод run

TestAppRoutes - тестирует Flask-роуты:

test_receive_data_success - проверяет успешную обработку валидных данных

test_receive_data_invalid_json - тестирует обработку невалидного JSON

test_receive_data_missing_fields - проверяет обработку запроса с отсутствующими полями
'''
