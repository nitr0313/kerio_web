from celery import shared_task
from django.contrib.auth import get_user_model
from django.conf import settings

from accounts.models import IPAddress, KerioGroup
from accounts.utils import KerioModuleAPI


User = get_user_model()


@shared_task
def sync_with_kerio_control():
    kerio = KerioModuleAPI()
    answer = kerio.get_trusted_ips()
    if not answer:
        return
    all_ips = list(IPAddress.objects.all())
    results = []
    for ip_object in all_ips:
        for user_in_kerio in answer:
            if ip_object.kerio_id == user_in_kerio['id']:
                ip_object.is_active = user_in_kerio['enabled']
                ip_object.ipaddress = user_in_kerio['host']
                ip_object.in_kerio = True
                results.append(ip_object)
    IPAddress.objects.bulk_update(results, fields=['ipaddress', 'is_active', 'in_kerio'])


@shared_task
def sync_in_from_kerio_control():
    """
    Забирает из керио все доверенные IP и создает модели
    с user = None, если модель с kerio_id уже есть в БД
    обновляет в ней данные
    :return:
    """
    kerio = KerioModuleAPI()
    answer = kerio.get_trusted_ips()
    if not answer:
        return
    result = {'updated': 0, 'created': 0}
    default_kerio_group = KerioGroup.objects.first()
    for user_in_kerio in answer:
        obj, create = IPAddress.objects.update_or_create(
            kerio_id=user_in_kerio['id'],
            defaults={
                'is_active': user_in_kerio['enabled'],
                'ipaddress': user_in_kerio['host'],
                'kerio_description': user_in_kerio['description'],
                'in_kerio': True,
                'kerio_group': default_kerio_group,
            }
        )
        if create:
            result['created'] += 1
            continue
        result['updated'] += 1
    return result


@shared_task
def change_user_ip_in_kerio(user_id):
    """
    Отправка данных в kerio при изменении IP или активкности правила
    """
    kerio = KerioModuleAPI()
    user = User.objects.get(id=user_id)
    count = settings.KERIO_MODULE_COUNT_TRY
    while count > 0:
        success = kerio.set_trusted_ip(user=user.ip_address)
        if not success:
            count -= 1
            continue
        ip_address = user.ip_address
        ip_address.in_kerio = True
        ip_address.save()
        break
