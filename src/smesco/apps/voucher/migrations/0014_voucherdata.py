# Generated by Django 2.1.1 on 2018-11-08 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voucher', '0013_delete_voucherdata'),
    ]

    operations = [
        migrations.CreateModel(
            name='VoucherData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_odr_amount', models.DecimalField(decimal_places=2, max_digits=20, verbose_name='Minimal Order Amount')),
            ],
        ),
    ]
