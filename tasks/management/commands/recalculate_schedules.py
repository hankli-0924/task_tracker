import logging

from django.core.management import BaseCommand

from tasks.models import Assignment
from tasks.services.scheduling_service import ScheduleService

logger = logging.getLogger('management.commands')  # 使用管理命令日志记录器


class Command(BaseCommand):
    help = 'Recalculate schedules for all team members based on dependency order.'

    def handle(self, *args, **options):
        logger.info('Starting schedule recalculation...')

        # try:
            # Get all assignments and determine the dependency order of team members
        assignments = Assignment.objects.select_related('task', 'team_member').filter(
            actual_start_time__isnull=True,
            actual_end_time__isnull=True,
            need_update=True)
        ordered_members = ScheduleService.get_team_member_dependency_order(assignments)

        # Reschedule each team member in dependency order
        for team_member in ordered_members:
            ScheduleService.reschedule_team_member(team_member)

        logger.info(self.style.SUCCESS('Schedule recalculation completed successfully.'))
        # except Exception as e:
        #     logger.info(self.style.ERROR(f'Error during schedule recalculation: {e}'))
