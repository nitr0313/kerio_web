from django.contrib import admin
from .models import IPAddress, KerioGroup


@admin.register(IPAddress)
class IPAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_active', 'in_kerio', 'user', 'ipaddress', 'kerio_description', 'updated')
    search_fields = ('user__username',)


@admin.register(KerioGroup)
class KerioGroupAdmin(admin.ModelAdmin):
    list_display = ('kerio_name', 'kerio_id')
