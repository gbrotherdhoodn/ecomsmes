# Generated by Django 2.1.1 on 2018-11-08 23:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voucher', '0015_delete_voucherdata'),
    ]

    operations = [
        migrations.CreateModel(
            name='VoucherDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('destination', models.IntegerField()),
            ],
        ),
    ]