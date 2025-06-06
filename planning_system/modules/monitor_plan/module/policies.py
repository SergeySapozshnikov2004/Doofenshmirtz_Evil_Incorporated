# Политики безопасности
policies = (
    {"src": "encryption_plan", "dst": "communicator"},
    {"src": "encryption_plan", "dst": "communication_module_plan"},
    {"src": "communicator", "dst": "communication_module_plan"},
    {"src": "communication_module_plan", "dst": "encryption_plan"},
    {"src": "communicator", "dst": "encryption_plan"}
)


def check_operation(id, details) -> bool:
    """ Проверка возможности совершения обращения. """
    src: str = details.get("source")
    dst: str = details.get("deliver_to")

    if not all((src, dst)):
        return False

    print(f"[info] checking policies for event {id}, {src}->{dst}")

    return {"src": src, "dst": dst} in policies