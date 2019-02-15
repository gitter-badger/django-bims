# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-02-08 02:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bims', '0114_datasource'),
        ('sass', '0033_sitevisittaxon_sass_taxon'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitevisit',
            name='data_source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bims.DataSource'),
        ),
    ]