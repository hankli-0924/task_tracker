from django.db import models
class VeriiiDefects(models.Model):
    id = models.TextField(primary_key=True)
    issue_description = models.TextField()
    owner = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    sys_name = models.TextField(blank=True, null=True)
    module_name = models.TextField(blank=True, null=True)
    priority = models.TextField(blank=True, null=True)
    priority_no = models.IntegerField(blank=True, null=True)
    workflow_status = models.TextField(blank=True, null=True)
    creation_time = models.DateField(blank=True, null=True)
    days_since_creation = models.IntegerField( blank=True, null=True)
    complete_time = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'veriii_defects'
