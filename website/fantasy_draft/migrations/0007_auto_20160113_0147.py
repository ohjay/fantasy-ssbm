# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-13 09:47
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('fantasy_draft', '0006_auto_20160112_0236'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userprofile',
            options={'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='key_expires',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 13, 9, 46, 59, 348075, tzinfo=utc)),
        ),
    ]
