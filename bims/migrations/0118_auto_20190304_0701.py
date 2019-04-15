# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-03-04 07:01
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('bims', '0117_auto_20190226_0646'),
    ]

    operations = [
        migrations.AddField(
            model_name='biologicalcollectionrecord',
            name='upstream_id',
            field=models.CharField(blank=True, help_text=b'Upstream id, e.g. Gbif key', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='biologicalcollectionrecord',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, help_text=b'Collection record uuid', null=True),
        ),
    ]