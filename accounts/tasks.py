from celery import shared_task
from django.contrib.auth import get_user_model
from django.conf import settings

from accounts.models import IPAddress, KerioGroup
from accounts.utils import RemoteModuleAPI, send_email_about_new_ip
from action_logger.service import ActionLoggerService

User = get_user_model()


@shared_task
def sync_in_from_kerio_control():
    """
    Забирает из керио все доверенные IP и создает модели
    с user = None, если модель с kerio_id уже есть в БД
    обновляет в ней данные
    :return:
    """
    kerio = RemoteModuleAPI()
    answer = kerio.get_all_users_ips()
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
    action = ActionLoggerService('Admin')
    action.sync_db()
    return result


@shared_task
def change_user_ip_in_router(user_id):
    """
    Отправка данных в kerio при изменении IP или активкности правила
    """
    kerio = RemoteModuleAPI()
    user = User.objects.get(id=user_id)
    count = settings.KERIO_MODULE_COUNT_TRY
    while count > 0:
        success = kerio.set_trusted_ip(user=user.ip_address)
        if not success:
            count -= 1
            continue
        ip_address = user.ip_address
        ip_address.in_router = True
        ip_address.save()
        action = ActionLoggerService(user)
        action.ip_updated_in_kerio(ip_address.ipaddress)
        return send_email_about_new_ip(user_id, user.ip_address.ipaddress)
