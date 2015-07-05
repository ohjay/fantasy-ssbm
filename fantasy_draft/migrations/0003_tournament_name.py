# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantasy_draft', '0002_auto_20150705_0616'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='name',
            field=models.CharField(default='[default]', max_length=20),
            preserve_default=False,
        ),
    ]
