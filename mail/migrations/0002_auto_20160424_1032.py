# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-24 05:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='status',
            field=models.CharField(default='1', max_length=1),
        ),
    ]