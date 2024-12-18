# Generated by Django 4.2.16 on 2024-11-05 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('talkpdf', '0004_alter_djcheckpoint_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='djcheckpoint',
            name='checkpoint',
            field=models.JSONField(),
        ),
        migrations.AlterField(
            model_name='djcheckpoint',
            name='metadata',
            field=models.JSONField(),
        ),
        migrations.AlterField(
            model_name='djwrite',
            name='value',
            field=models.JSONField(blank=True, default=None, null=True),
        ),
    ]
