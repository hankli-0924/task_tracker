from django.db import models
class VeriiiTaskAssignments(models.Model):
    # id = models.BigIntegerField(blank=True, null=True)
    task_name = models.CharField(max_length=255, blank=True, null=True)
    priority = models.TextField(blank=True, null=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    planed_start_time = models.DateTimeField(blank=True, null=True)
    planed_end_time = models.DateTimeField(blank=True, null=True)
    planned_verification_time = models.DateTimeField(blank=True, null=True)
    effort_estimation_in_man_days = models.DecimalField(max_digits=5,
                                                        decimal_places=2,
                                                        blank=True,
                                                        null=True)
    actual_start_time = models.DateTimeField(blank=True, null=True)
    actual_end_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'veriii_task_assignments'
