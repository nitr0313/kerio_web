from django.db import models


class ActionLogger(models.Model):
    msg = models.CharField(max_length=1000, verbose_name="Лог")
    created = models.DateTimeField(auto_now_add=True)

