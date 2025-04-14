import unittest
from unittest.mock import patch, MagicMock
from autopilot import Status, Autopilot, app
import json

class TestStatus(unittest.TestCase):
    def setUp(self):
        self.valid_status = {
            "motor_system_status": True,
            "jet_system_status": True,
            "photo_sensor_status": True,
            "car_status": True,
            "fast_reaction_system_status": True
        }
        self.mode = "Driving"
    
    def test_status_correct_all_true(self):
        status = Status(self.valid_status, self.mode)
        self.assertTrue(status.status_correct())
    
    def test_status_correct_with_false(self):
        broken_status = self.valid_status.copy()
        broken_status["motor_system_status"] = False
        status = Status(broken_status, self.mode)
        self.assertFalse(status.status_correct())
    
    def test_check_mode_driving(self):
        status = Status(self.valid_status, "Driving")
        self.assertTrue(status.check_mode())
    
    def test_check_mode_sleep(self):
        status = Status(self.valid_status, "Sleep_mode")
        self.assertFalse(status.check_mode())
    
    def test_get_mode(self):
        status = Status(self.valid_status, "Test_mode")
        self.assertEqual(status.get_mode(), "Test_mode")

class TestAutopilot(unittest.TestCase):
    def setUp(self):
        self.coordinates = {'X': 0, 'Y': 0}
        self.direction = [2, 2, 1, 3]  # right, right, up, left
        self.mock_status = MagicMock()
        self.mock_status.status_correct.return_value = True
        self.mock_status.check_mode.return_value = True
        self.mock_status.get_mode.return_value = "Driving"
    
    def test_drive_changes_coordinates(self):
        autopilot = Autopilot(self.coordinates.copy(), self.direction, self.mock_status)
        autopilot.drive()
        self.assertEqual(autopilot.coordinates, {'X': 1, 'Y': 1})
    
    def test_run_calls_drive_and_generate_status(self):
        with patch.object(Autopilot, 'drive') as mock_drive, \
             patch.object(Autopilot, 'generate_status') as mock_generate:
            autopilot = Autopilot(self.coordinates.copy(), self.direction, self.mock_status)
            autopilot.run()
            mock_drive.assert_called_once()
            mock_generate.assert_called_once()
    
    def test_send_command_returns_success(self):
        autopilot = Autopilot(self.coordinates.copy(), self.direction, self.mock_status)
        with app.test_request_context():
            response = autopilot.send_command()
            response_data = json.loads(response.get_data(as_text=True))
            self.assertEqual(response_data, {"status": "success"})

class TestAppRoutes(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.valid_data = {
            "coordinates": {'X': 0, 'Y': 0},
            "direction": [2, 2, 1, 3]
        }
    
    def test_receive_operation_success(self):
        response = self.app.post(
            '/report',
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response_data["status"], "success")
    
    def test_receive_operation_invalid_json(self):
        response = self.app.post(
            '/report',
            data="invalid json",
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    @patch('autopilot.Autopilot')
    def test_receive_operation_calls_autopilot(self, mock_autopilot):
        mock_instance = mock_autopilot.return_value
        mock_instance.run.return_value = None
        mock_instance.send_command.return_value = {"status": "success"}
        
        response = self.app.post(
            '/report',
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )
        
        mock_autopilot.assert_called_once_with(
            coordinates=self.valid_data["coordinates"],
            direction=self.valid_data["direction"],
            status=None
        )
        mock_instance.run.assert_called_once()
        mock_instance.send_command.assert_called_once()

if __name__ == '__main__':
    unittest.main()
'''
Пояснения к тестам:
TestStatus - тестирует класс Status:

Проверяет корректность работы status_correct() при разных состояниях систем

Тестирует проверку режима работы (check_mode())

Проверяет получение текущего режима (get_mode())

TestAutopilot - тестирует класс Autopilot:

Проверяет корректность изменения координат при движении

Проверяет вызов необходимых методов при работе (run())

Тестирует отправку команды (send_command())

TestAppRoutes - тестирует Flask-роуты:

Проверяет успешную обработку валидного запроса

Проверяет обработку невалидного JSON

Мокирует Autopilot для проверки корректности вызовов
'''
