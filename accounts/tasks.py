from celery import shared_task

from accounts.models import IPAddress
from accounts.utils import KerioModuleAPI


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
