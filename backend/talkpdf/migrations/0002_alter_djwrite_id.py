# Generated by Django 4.2.16 on 2024-10-09 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('talkpdf', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='djwrite',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
