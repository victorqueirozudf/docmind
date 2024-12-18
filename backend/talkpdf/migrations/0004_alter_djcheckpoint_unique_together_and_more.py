# Generated by Django 4.2.16 on 2024-11-05 15:11

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('talkpdf', '0003_alter_chatdetails_thread_id'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='djcheckpoint',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='djwrite',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='djcheckpoint',
            name='chat',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='checkpoints', to='talkpdf.chatdetails'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='djwrite',
            name='chat',
            field=models.ForeignKey(default=123, on_delete=django.db.models.deletion.CASCADE, related_name='writes', to='talkpdf.chatdetails'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='chatdetails',
            name='thread_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='djcheckpoint',
            unique_together={('chat', 'thread_ts')},
        ),
        migrations.AlterUniqueTogether(
            name='djwrite',
            unique_together={('chat', 'thread_ts', 'task_id', 'idx')},
        ),
        migrations.RemoveField(
            model_name='djcheckpoint',
            name='thread_id',
        ),
        migrations.RemoveField(
            model_name='djwrite',
            name='thread_id',
        ),
    ]
