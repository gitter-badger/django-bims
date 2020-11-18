# Generated by Django 2.2.12 on 2020-11-18 03:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0022_uploadedimage'),
        ('bims', '0271_auto_20201112_0409'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpage',
            name='intro_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image'),
        ),
    ]
