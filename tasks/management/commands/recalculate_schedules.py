import logging

from django.core.management import BaseCommand

from tasks.models import Assignment, TeamMember
from tasks.services.scheduling_service import ScheduleService

logger = logging.getLogger('management.commands')  # 使用管理命令日志记录器


class Command(BaseCommand):
    help = 'Recalculate schedules for all team members based on dependency order.'

    def handle(self, *args, **options):
        logger.info('Starting schedule recalculation...')


        # 获取所有唯一且符合条件的team_member ID
        team_member_ids = Assignment.objects.filter(
            actual_start_time__isnull=True,
            actual_end_time__isnull=True,
            effort_estimation__isnull=False
        ).values_list('team_member', flat=True).distinct()

        # 使用这些ID来获取对应的team_member对象
        unique_team_members = TeamMember.objects.filter(id__in=team_member_ids)

        # Reschedule each team member in dependency order
        for team_member in unique_team_members:
            ScheduleService.reschedule_team_member(team_member)
            logger.info(self.style.SUCCESS(f'reschedule_team_member for {team_member} successfully.'))

        logger.info(self.style.SUCCESS('Schedule recalculation completed successfully.'))



if __name__ == '__main__':
    Command().handle()