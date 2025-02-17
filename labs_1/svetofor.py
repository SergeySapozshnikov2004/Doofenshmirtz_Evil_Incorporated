import pdb
from multiprocessing import Queue
monitor_events_queue = Queue()

from dataclasses import dataclass


@dataclass
class Event:
    source: str       # отправитель
    destination: str  # получатель
    operation: str    # чего хочет (запрашиваемое действие)
    parameters: str   # с какими параметрами

from multiprocessing import Queue, Process
from multiprocessing.queues import Empty
import json

# формат управляющих команд для монитора
@dataclass
class ControlEvent:
    operation: str

# список разрешенных сочетаний сигналов светофора
# любые сочетания, отсутствующие в этом списке, запрещены
traffic_lights_allowed_configurations = [
    {"direction_1": "red", "direction_2": "green"},
    {"direction_1": "red", "direction_2": "red"},    
    {"direction_1": "red", "direction_2": "yellow"},    
    {"direction_1": "yellow", "direction_2": "yellow"},    
    {"direction_1": "off", "direction_2": "off"},
    {"direction_1": "green", "direction_2": "red"},    
    {"direction_1": "green", "direction_2": "yellow"},
]

traffic_lights_unregulated_configurations = [
    {"direction_1": "red", "direction_2": "yellow_blinking"},
    {"direction_1": "yellow", "direction_2": "yellow_blinking"},
    {"direction_1": "green", "direction_2": "yellow_blinking"},    
]

turn_configuration = [
    {"direction_1": "red", "direction_2": "green"},
    {"direction_1": "green", "direction_2": "red"},
]

status_configuration = [
    {"status": "correct"},
]


# Класс, реализующий поведение монитора безопасности
class Monitor(Process):

    def __init__(self, events_q: Queue):
        # вызываем конструктор базового класса
        super().__init__()
        self._events_q = events_q  # очередь событий для монитора (входящие сообщения)
        self._control_q = Queue()  # очередь управляющих команд (например, для остановки монитора)
        self._entity_queues = {}   # словарь очередей известных монитору сущностей
        self._force_quit = False   # флаг завершения работы монитора

    # регистрация очереди новой сущности
    def add_entity_queue(self, entity_id: str, queue: Queue):
        print(f"[монитор] регистрируем сущность {entity_id}")
        self._entity_queues[entity_id] = queue

    def _check_mode(self, mode_str: str) -> bool:
        mode_ok = False
        try:
            # извлечём структуру из строки, в случае ошибки запретим изменение режима
            mode = json.loads(mode_str[0])
            mode_left = json.loads(mode_str[1])
            mode_right = json.loads(mode_str[2])
            # проверим входит ли запрашиваемый режим в список разрешённых
            print(f"[монитор] проверяем конфигурацию светофора {mode}")
            print(f"[монитор] проверяем конфигурацию левой стрелки {mode}")
            print(f"[монитор] проверяем конфигурацию правой стрелки {mode}")
            if (mode in traffic_lights_allowed_configurations and mode_left in turn_configuration and mode_right in turn_configuration 
            or mode in traffic_lights_unregulated_configurations and mode_left in turn_configuration and mode_right in turn_configuration
            or mode in status_configuration and mode_left in status_configuration and mode_right in status_configuration):
                # такой режим найден, можно активировать
                mode_ok = True
        except:
            mode_ok = False
        return mode_ok

    # проверка политик безопасности        
    def _check_policies(self, event):
        print(f'[монитор] обрабатываем событие {event}')

        # default deny: всё, что не разрешено, запрещено по умолчанию!
        authorized = False

        # проверка на входе, что это экземпляр класса Event, 
        # т.е. имеет ожидаемый формат
        if not isinstance(event, Event):
            return False

        # 
        #  политики безопасности
        #

        # пример политики безопасности
        if event.source == "ControlSystem" \
                and event.destination == "LightsGPIO" \
                and event.operation == "set_mode" \
                and self._check_mode(event.parameters):
            authorized = True

        if event.source == "LightsGPIO" \
                and event.destination == "SelfDiagnostics" \
                and event.operation == "diagnostics_input" \
                and self._check_mode(event.parameters):
            authorized = True


        if event.source == "SelfDiahnostics" \
                and event.destination == "ControlSystem" \
                and event.operation == "diagnostics_output" \
                and self._check_mode(event.parameters):
            authorized = True

        if authorized is False:
            print("[монитор] событие не разрешено политиками безопасности")
        return authorized

    # выполнение разрешённого запроса
    # метод должен вызываться только после проверки политик безопасности
    def _proceed(self, event):
        print(f'[монитор] отправляем запрос {event}')
        try:
            # найдём очередь получателя события
            dst_q: Queue = self._entity_queues[event.destination]
            # и положим запрос в эту очередь
            dst_q.put(event)
        except  Exception as e:
            # например, запрос пришёл от или для неизвестной сущности
            print(f"[монитор] ошибка выполнения запроса {e}")

    # основной код работы монитора безопасности    
    def run(self):
        #while True: 
            print('[монитор] старт')
    
            # в цикле проверяет наличие новых событий, 
            # выход из цикла по флагу _force_quit
            while self._force_quit is False:
                event = None
                try:
                    # ожидание сделано неблокирующим, 
                    # чтобы можно было завершить работу монитора, 
                    # не дожидаясь нового сообщения
                    event = self._events_q.get_nowait()
                    # сюда попадаем только в случае получение события,
                    # теперь нужно проверить политики безопасности
                    authorized = self._check_policies(event)
                    if authorized:
                        # если политиками запрос авторизован - выполняем
                        self._proceed(event)
                except Empty:
                    # сюда попадаем, если новых сообщений ещё нет,
                    # в таком случае немного подождём
                    sleep(0.5)
                except Exception as e:
                    # что-то пошло не так, выведем сообщение об ошибке
                    print(f"[монитор] ошибка обработки {e}, {event}")
                self._check_control_q()
            print('[монитор] завершение работы')
            sleep(2)

    # запрос на остановку работы монитора безопасности для завершения работы
    # может вызываться вне процесса монитора
    def stop(self):
        # поскольку монитор работает в отдельном процессе,
        # запрос помещается в очередь, которая проверяется из процесса монитора
        request = ControlEvent(operation='stop')
        self._control_q.put(request)

    # проверка наличия новых управляющих команд
    def _check_control_q(self):
        try:
            request: ControlEvent = self._control_q.get_nowait()
            print(f"[монитор] проверяем запрос {request}")
            if isinstance(request, ControlEvent) and request.operation == 'stop':
                # поступил запрос на остановку монитора, поднимаем "красный флаг"
                self._force_quit = True
        except Empty:
            # никаких команд не поступило, ну и ладно
            pass


from multiprocessing import Queue, Process
import json


class ControlSystem(Process):

    def __init__(self, monitor_queue: Queue):
        # вызываем конструктор базового класса
        super().__init__()
        # мы знаем только очередь монитора безопасности для взаимодействия с другими сущностями
        # прямая отправка сообщений в другую сущность запрещена в концепции FLASK
        self.monitor_queue = monitor_queue
        # создаём собственную очередь, в которую монитор сможет положить сообщения для этой сущности
        self._own_queue = Queue()

    # выдаёт собственную очередь для взаимодействия
    def entity_queue(self):
        return self._own_queue

    # основной код сущности
    def run(self): 
        print(f'[{self.__class__.__name__}] старт')

        mode = {"direction_1": "red", "direction_2": "yellow_blinking"}
        turn_left_mode = {"direction_1": "red", "direction_2": "green"}
        turn_right_mode = {"direction_1": "green", "direction_2": "red"}
        # запрос для сущности WorkerB - "скажи hello"
        event = Event(source=self.__class__.__name__,
                              destination='LightsGPIO',
                              operation='set_mode',
                              parameters=[json.dumps(mode),
                                          json.dumps(turn_left_mode), 
                                          json.dumps(turn_right_mode),
                                         ]
                              )
        self.monitor_queue.put(event)
        print(f'[{self.__class__.__name__}] завершение работы')
        self.monitor_queue.put(event)
        print(f'[{self.__class__.__name__}] завершение работы')




from multiprocessing import Queue, Process
from time import sleep


class LightsGPIO(Process):

    def __init__(self, monitor_queue: Queue):
        # вызываем конструктор базового класса
        super().__init__()
        # мы знаем только очередь монитора безопасности для взаимодействия с другими сущностями
        # прямая отправка сообщений в другую сущность запрещена в концепции FLASK
        self.monitor_queue = monitor_queue
        
        # создаём собственную очередь, в которую монитор сможет положить сообщения для этой сущности
        self._own_queue = Queue()

    def entity_queue(self):
        return self._own_queue

    # основной код сущности
    def run(self):  
        #while True:      
            print(f'[{self.__class__.__name__}] старт')
            attempts = 10
            while attempts > 0:
                try:
                    event: Event = self._own_queue.get_nowait()
                    if event.operation == "set_mode":
                        print(f"[{self.__class__.__name__}] {event.source} запрашивает изменение режима светофора {event.parameters[0]}")
                        print(f"[{self.__class__.__name__}] {event.source} запрашивает изменение режима левой стрелки {event.parameters[1]}")
                        print(f"[{self.__class__.__name__}] {event.source} запрашивает изменение режима правой стрелки {event.parameters[2]}")
                        mode = json.loads(event.parameters[0])
                        mode_left = json.loads(event.parameters[1])
                        mode_right = json.loads(event.parameters[2])

                        if mode in traffic_lights_unregulated_configurations:
                            print(f"[{self.__class__.__name__}] новый режим светофора: {event.parameters[0]} не регулируемый!")
                        else:
                            print(f"[{self.__class__.__name__}] новый режим светофора: {event.parameters[0]} регулируемый!")
                        print(f"[{self.__class__.__name__}] новый режим левой стрелки: {event.parameters[1]}!")
                        print(f"[{self.__class__.__name__}] новый режим правой стрелки: {event.parameters[2]}!")
                        break
                except Empty:
                    sleep(2)
                    attempts -= 1

            status = {"status": "correct"}
            event = Event(source=self.__class__.__name__,
                          destination='SelfDiagnostics',
                          operation='diagnostics_input',
                          parameters=[json.dumps(status),
                                     json.dumps(status), 
                                     json.dumps(status)
                          ])

            self.monitor_queue.put(event)
            print(f'[{self.__class__.__name__}] завершение работы')

class SelfDiagnostics(Process):
    def __init__(self, monitor_queue):
        super().__init__()
        self.monitor_queue = monitor_queue
        self._own_queue = Queue()

    def entity_queue(self):
        return self._own_queue

    def run(self):
        print(f'[{self.__class__.__name__}] старт')
        attempts = 3
        while attempts > 0:
            try:
                event: Event = self._own_queue.get_nowait()
                svetofor_status = json.loads(event.parameters[0])
                left_status = json.loads(event.parameters[1])
                right_status = json.loads(event.parameters[2])
                print(f"[{self.__class__.__name__}] статус светофора: {event.parameters[0]}")
                print(f"[{self.__class__.__name__}] статус левой стрелки: {event.parameters[1]}")
                print(f"[{self.__class__.__name__}] статус правой стрелки: {event.parameters[2]}")
                       
            except Empty:
                    sleep(2)
                    attempts -= 1
        
        event = Event(source=self.__class__.__name__,
                          destination='ControlSystem',
                          operation='diagnostics_output',
                          parameters=[{"status": "correct"},
                                      {"status": "correct"},
                                      {"status": "correct"},
                                     ]
                          )

        self.monitor_queue.put(event)
        print(f'[{self.__class__.__name__}] завершение работы')


monitor = Monitor(monitor_events_queue)
control_system = ControlSystem(monitor_events_queue)
lights_gpio = LightsGPIO(monitor_events_queue)
self_diagnostics = SelfDiagnostics(monitor_events_queue)



monitor.add_entity_queue(control_system.__class__.__name__, control_system.entity_queue())
monitor.add_entity_queue(lights_gpio.__class__.__name__, lights_gpio.entity_queue())
monitor.add_entity_queue(self_diagnostics.__class__.__name__, self_diagnostics.entity_queue())



monitor.start()

control_system.start()
lights_gpio.start()

sleep(2)
self_diagnostics.start()

sleep(2)
monitor.stop()
control_system.join()
lights_gpio.join()
self_diagnostics.join()
monitor.join()