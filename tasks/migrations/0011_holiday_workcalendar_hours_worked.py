# Generated by Django 5.1.4 on 2024-12-28 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0010_taskpredecessor_task_predecessors'),
    ]

    operations = [
        migrations.CreateModel(
            name='Holiday',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
                ('name', models.CharField(help_text='Name of the holiday', max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='workcalendar',
            name='hours_worked',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Actual hours worked on this day', max_digits=4, null=True),
        ),
    ]
