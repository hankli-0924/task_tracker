# Generated by Django 5.1.4 on 2024-12-29 06:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0012_remove_historicaltask_workload_remove_task_workload'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ['level', 'priority', 'created_at']},
        ),
        migrations.AlterField(
            model_name='assignment',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='tasks.task'),
        ),
    ]
