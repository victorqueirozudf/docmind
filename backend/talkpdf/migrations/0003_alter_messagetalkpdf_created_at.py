# Generated by Django 4.2.16 on 2024-09-25 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('talkpdf', '0002_messagetalkpdf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messagetalkpdf',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]