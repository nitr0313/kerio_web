from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
User = get_user_model()


# Create your models here.

class IPAddress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ipaddress = models.CharField(max_length=15, verbose_name=_("IP address"), default="0.0.0.0")
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    in_kerio = models.BooleanField(default=False, verbose_name=_("Applied in Kerio"))
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    kerio_id = models.CharField(max_length=5, null=True, blank=True, default=None, verbose_name=_("ID in KerioControl"))
    kerio_group = models.ForeignKey("KerioGroup", on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = _("IP address")
        verbose_name_plural = _("IP addresses")
        ordering = ('id',)

    def __str__(self):
        return f"{self.user} {self.ipaddress}"


class KerioGroup(models.Model):
    kerio_id = models.CharField(max_length=200, default="", verbose_name=_("Group id in KerioControl"))
    kerio_name = models.CharField(max_length=1000, default="", verbose_name=_("Group description in KerioControl"))

    class Meta:
        verbose_name = _("IP address group")
        verbose_name_plural = _("IP addresses groups")
        ordering = ('kerio_name',)

    def __str__(self):
        return f"{self.kerio_name}"
