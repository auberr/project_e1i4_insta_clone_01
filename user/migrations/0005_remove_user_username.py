# Generated by Django 3.2.15 on 2022-10-03 12:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_user_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
    ]
