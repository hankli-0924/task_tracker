# Generated by Django 5.1.4 on 2024-12-28 06:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0006_historicaltask_level_task_level'),
    ]

    operations = [
        migrations.RunSQL('''
        update tasks_task set real_priority = substr(priority,2)::numeric ;
        ''')
    ]
