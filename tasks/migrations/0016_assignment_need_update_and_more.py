# Generated by Django 5.1.4 on 2025-01-01 01:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0015_rename_real_priority_historicaltask_priority_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='need_update',
            field=models.BooleanField(default=False, help_text='Need update?'),
        ),
        migrations.AddField(
            model_name='historicalassignment',
            name='need_update',
            field=models.BooleanField(default=False, help_text='Need update?'),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='effort_estimation',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Estimated effort in man days', max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='historicalassignment',
            name='effort_estimation',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Estimated effort in man days', max_digits=5, null=True),
        ),
    ]
