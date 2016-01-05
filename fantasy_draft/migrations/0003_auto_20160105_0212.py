# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-05 10:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasy_draft', '0002_auto_20160105_0047'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_turn',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='bid',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
