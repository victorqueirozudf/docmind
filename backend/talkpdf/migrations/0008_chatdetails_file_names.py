# Generated by Django 4.2.16 on 2024-11-22 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('talkpdf', '0007_rename_djcheckpoint_chatcheckpoint_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatdetails',
            name='file_names',
            field=models.JSONField(default=list),
        ),
    ]
