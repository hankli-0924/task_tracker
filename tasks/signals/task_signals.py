from django.db.models.signals import post_save
from django.dispatch import receiver
from tasks.models import Task, Assignment, WorkCalendar
from tasks.services.scheduling_service import recalculate_all_assignments_schedule


@receiver(post_save, sender=Assignment)
@receiver(post_save, sender=Task)
@receiver(post_save, sender=WorkCalendar)
def trigger_recalculation(sender, instance, **kwargs):
    if isinstance(instance, Assignment) or isinstance(instance, Task):
        team_member = instance.team_member if isinstance(instance,
                                                         Assignment) else instance.assignments.first().team_member
    elif isinstance(instance, WorkCalendar):
        team_member = instance.team_member

    if team_member:
        recalculate_all_assignments_schedule(team_member)
