# Generated by Django 2.2.12 on 2020-10-16 02:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bims', '0262_auto_20201009_0639'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesetting',
            name='base_country_code',
            field=models.CharField(blank=True, default='', help_text='Base country code for the site, using ISO 3166-1 (See here for the list : https://wiki.openstreetmap.org/wiki/Nominatim/Country_Codes)', max_length=100),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='site_code_generator',
            field=models.CharField(blank=True, choices=[('bims', 'BIMS (2 Site Name + 2 Site Description + Site count)'), ('fbis', 'FBIS (2 Secondary catchment + 4 River + Site count)'), ('rbis', 'RBIS (1 Catchment 0 + 2 Catchment 1 + 1 Catchment 2 + Site count)')], default='bims', help_text='How site code generated', max_length=50),
        ),
    ]
