# Generated by Django 2.2.28 on 2022-05-17 06:56

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bims', '0306_auto_20220428_0506'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='uuid',
            field=models.CharField(blank=True, help_text='Survey uuid', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='uploadsession',
            name='category',
            field=models.CharField(blank=True, choices=[('taxa', 'Taxa'), ('collections', 'Collections'), ('water_temperature', 'Water Temperature'), ('physico_chemical', 'Physico Chemical')], default='', max_length=50),
        ),
    ]
