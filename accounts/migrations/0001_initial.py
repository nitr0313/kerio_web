# Generated by Django 4.0.5 on 2022-06-30 07:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='KerioGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kerio_id', models.CharField(default='', max_length=200, verbose_name='Group id in KerioControl')),
                ('kerio_name', models.CharField(default='', max_length=1000, verbose_name='Group description in KerioControl')),
            ],
            options={
                'verbose_name': 'IP address group',
                'verbose_name_plural': 'IP addresses groups',
                'ordering': ('kerio_name',),
            },
        ),
        migrations.CreateModel(
            name='IPAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ipaddress', models.CharField(max_length=15, null=True, verbose_name='IP address')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('in_kerio', models.BooleanField(default=False, verbose_name='Applied in Kerio')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('kerio_id', models.CharField(blank=True, default=None, max_length=5, null=True, verbose_name='ID in KerioControl')),
                ('kerio_group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.keriogroup')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'IP address',
                'verbose_name_plural': 'IP addresses',
                'ordering': ('id',),
            },
        ),
    ]
