# Generated by Django 4.0.5 on 2022-07-27 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_ipaddress_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ipaddress',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Is active'),
        ),
    ]