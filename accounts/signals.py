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
