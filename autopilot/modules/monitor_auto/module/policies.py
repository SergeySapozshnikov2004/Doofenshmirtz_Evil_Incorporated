# Политики безопасности
policies = (
    {"src": "intelligent_engine_control_system", "dst": "electric_motors"},
    {"src": "electric_motors", "dst": "intelligent_engine_control_system"},
    {"src": "intelligent_engine_control_system", "dst": "jet_engine"},
    {"src": "jet_engine", "dst": "intelligent_engine_control_system"},
    {"src": "control_route", "dst": "emergency_scenario"},
    {"src": "emergency_scenario", "dst": "braking_system"},
    {"src": "cameras", "dst": "machine-vision"},
    {"src": "machine-vision", "dst": "proccesing_unit"},
    {"src": "lidar", "dst": "proccesing_unit"},
    {"src": "infrared_sensors", "dst": "proccesing_unit"},
    {"src": "proccesing_unit", "dst": "calculation_accident_avoidance_trajectory"},
    {"src": "proccesing_unit", "dst": "calculation_accident_avoidance_trajectory"},
    {"src": "calculation_accident_avoidance_trajectory", "dst": "route_control"})
    


def check_operation(id, details) -> bool:
    """ Проверка возможности совершения обращения. """
    src: str = details.get("source")
    dst: str = details.get("deliver_to")

    if not all((src, dst)):
        return False

    print(f"[info] checking policies for event {id}, {src}->{dst}")

    return {"src": src, "dst": dst} in policies