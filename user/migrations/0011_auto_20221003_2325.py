# Generated by Django 3.2.15 on 2022-10-03 14:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_user_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={},
        ),
        migrations.AlterModelTable(
            name='user',
            table='User',
        ),
    ]
