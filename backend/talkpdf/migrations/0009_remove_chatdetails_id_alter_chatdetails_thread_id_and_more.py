# Generated by Django 4.2.16 on 2024-10-09 11:36

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('talkpdf', '0008_djcheckpoint_id_alter_chatdetails_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatdetails',
            name='id',
        ),
        migrations.AlterField(
            model_name='chatdetails',
            name='thread_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='djcheckpoint',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='djcheckpoint',
            name='thread_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='talkpdf.chatdetails'),
        ),
    ]
