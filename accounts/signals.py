from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import IPAddress
from .utils import KerioModuleAPI

User = get_user_model()


@receiver(post_save, sender=User)
def create_ipaddress_object(sender, instance, *args, **kwargs):
    """
    Создание Объекта IPAddress при создании пользователя
    """
    obj_ = IPAddress.objects.filter(user=instance).first()
    if obj_ is None:
        IPAddress.objects.create(user=instance)


@receiver(pre_save, sender=IPAddress)
def change_user_ip_in_kerio(sender, instance, *args, **kwargs):
    """
    Отправка данных в kerio при изменении IP или активкности правила
    """
    old_ip = IPAddress.objects.filter(user=instance.user).first()
    if old_ip is None or instance.ipaddress == "0.0.0.0":
        return
    if old_ip.ipaddress != instance.ipaddress or old_ip.is_active != instance.is_active:
        kerio = KerioModuleAPI()
        answer = kerio.set_trusted_ip(user=instance)
        if 'errors' in answer and not answer['errors']:
            instance.in_kerio = True
