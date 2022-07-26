from django.contrib.auth.models import User
from accounts.models import IPAddress
from accounts.tasks import change_user_ip_in_kerio


class KerioService:
    def __init__(self, user: User):
        self.user = user

    def get_ip_from_db(self) -> IPAddress:
        """
        Получить адрес из БД
        :return:
        """
        return IPAddress.objects.filter(user=self.user).first()

    def change_object_in_db(self, new_ip: str = None, is_active: bool = None):
        """
        Изменить ip пользователя в базе
        :param new_ip: str - новый Ip адресс пользователя
        :param is_active: bool - активность правила доступа
        :return:
        """
        ip_object = self.get_ip_from_db()
        if new_ip is not None and new_ip != ip_object.ipaddress:
            ip_object.ipaddress = new_ip
            ip_object.in_kerio = False
        if is_active is not None and is_active != ip_object.is_active:
            ip_object.is_active = is_active
            ip_object.in_kerio = False
        if any([new_ip, is_active]):
            ip_object.save()
            change_user_ip_in_kerio.delay(self.user.id)
        return ip_object

    def get_all_ip_in_db(self):
        if self.user.is_staff:
            return IPAddress.objects.all()
