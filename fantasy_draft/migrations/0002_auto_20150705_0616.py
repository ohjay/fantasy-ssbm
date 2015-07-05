# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('fantasy_draft', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('identifier', models.CharField(max_length=20)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('date', models.DateField(verbose_name='tournament date')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TournamentResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('player_tag', models.CharField(max_length=30)),
                ('placing', models.IntegerField(max_length=4)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=30)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='tournament',
            name='results',
            field=models.ManyToManyField(to='fantasy_draft.TournamentResult'),
            preserve_default=True,
        ),
        migrations.RenameField(
            model_name='player',
            old_name='gamer_tag',
            new_name='tag',
        ),
        migrations.RemoveField(
            model_name='league',
            name='num_drafts',
        ),
        migrations.AddField(
            model_name='league',
            name='date_created',
            field=models.DateTimeField(verbose_name='date created', default=datetime.datetime(2015, 7, 5, 6, 15, 19, 530415, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='league',
            name='name',
            field=models.CharField(max_length=30, default='default_name'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='player',
            name='description',
            field=models.TextField(default='default_desc'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='player',
            name='picture',
            field=models.ImageField(upload_to='player_images', default='default pic'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='player',
            name='placing',
            field=models.IntegerField(max_length=4, default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='player',
            name='pool',
            field=models.ForeignKey(default=1, to='fantasy_draft.Pool'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='player',
            name='seed',
            field=models.IntegerField(max_length=4, default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='player',
            name='tournaments',
            field=models.ManyToManyField(to='fantasy_draft.Tournament'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='draft',
            name='user',
            field=models.ForeignKey(to='fantasy_draft.User'),
            preserve_default=True,
        ),
    ]
