# Generated by Django 2.2.12 on 2021-04-21 05:48

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bims', '0289_remove_biologicalcollectionrecord_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadsession',
            name='error_file',
            field=models.FileField(blank=True, max_length=512, null=True, upload_to='taxa-file/'),
        ),
        migrations.AlterField(
            model_name='uploadsession',
            name='process_file',
            field=models.FileField(max_length=512, null=True, upload_to='taxa-file/'),
        ),
        migrations.AlterField(
            model_name='uploadsession',
            name='success_file',
            field=models.FileField(blank=True, max_length=512, null=True, upload_to='taxa-file/'),
        ),
        migrations.AlterField(
            model_name='uploadsession',
            name='updated_file',
            field=models.FileField(blank=True, max_length=512, null=True, upload_to='taxa-file/'),
        ),
    ]