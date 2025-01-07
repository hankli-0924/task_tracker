from django.db import models


class AllCompletionWork(models.Model):
    task_type = models.TextField(blank=True, null=True)
    issue_description = models.TextField(blank=True, null=True)
    owner = models.TextField(blank=True, null=True)
    complete_time = models.DateTimeField(blank=True, null=True)
    days_spent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'all_completion_work'
