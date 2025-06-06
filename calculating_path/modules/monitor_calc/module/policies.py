# Политики безопасности
policies = (
    {"src": "communication_module", "dst": "encryption"},
    {"src": "encryption", "dst": "algorithm_calculating_path"},
    {"src": "GPS_Glonass", "dst": "calculating_the_optimal_path"},
    {"src": "inertial_reference_frame", "dst": "calculating_the_optimal_path"},
    {"src": "calculating_the_optimal_path", "dst": "algorithm_calculating_path"},
    {"src": "algorithm_calculating_path", "dst": "calculating_the_optimal_path"}
)


def check_operation(id, details) -> bool:
    """ Проверка возможности совершения обращения. """
    src: str = details.get("source")
    dst: str = details.get("deliver_to")

    if not all((src, dst)):
        return False

    print(f"[info] checking policies for event {id}, {src}->{dst}")

    return {"src": src, "dst": dst} in policies