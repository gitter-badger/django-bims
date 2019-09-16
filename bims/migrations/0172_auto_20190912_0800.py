# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-09-12 08:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bims', '0171_sitesetting_default_data_source'),
    ]

    operations = [
        migrations.AddField(
            model_name='biotope',
            name='broad',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='biotope',
            name='specific',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='biotope',
            name='substratum',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
