# Generated by Django 2.0 on 2019-01-13 13:18

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0006_auto_20181003_1752'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraddress',
            name='phone',
            field=models.CharField(blank=True, max_length=14, null=True, validators=[django.core.validators.RegexValidator(message='field harus number dengan minimal 8 nomor dan tidak lebih dari 14', regex='^\\d{8,14}$')], verbose_name='Nomor Telpon/Hp'),
        ),
    ]