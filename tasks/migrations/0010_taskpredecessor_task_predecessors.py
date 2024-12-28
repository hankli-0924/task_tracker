# Generated by Django 5.1.4 on 2024-12-28 07:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0009_alter_task_options_historicaltask_workload_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskPredecessor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('established_on', models.DateTimeField(auto_now_add=True)),
                ('from_task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_predecessors', to='tasks.task')),
                ('to_task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_successors', to='tasks.task')),
            ],
            options={
                'unique_together': {('from_task', 'to_task')},
            },
        ),
        migrations.AddField(
            model_name='task',
            name='predecessors',
            field=models.ManyToManyField(blank=True, related_name='successors', through='tasks.TaskPredecessor', to='tasks.task'),
        ),
    ]
