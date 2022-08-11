from .models import ActionLogger


class ActionLoggerService:
    model = ActionLogger

    def __init__(self, user):
        self.user = user

    def change_ip(self, old_ip, new_ip, old_state, new_state):
        self.create_obj(
            f"{self.user} меняет СОСТОЯНИЕ / IP:"
            f"{'ON' if old_state else 'OFF'} / {old_ip} на {'ON' if new_state else 'OFF'} / {new_ip}")

    def ip_updated_in_kerio(self, new_ip):
        self.create_obj(f"IP адрес пользователя <{self.user}> обновился в kerio на {new_ip}")

    def add_task_sync_db(self):
        self.create_obj(f"{self.user} Создал задачу синхронизации")

    def sync_db(self):
        self.create_obj(f"{self.user} Задача выполенна успешно")

    def get_logs(self, last: int = None):
        return list(self.model.objects.all().order_by('-created'))[:last]

    def create_obj(self, msg):
        self.model.objects.create(msg=msg)
