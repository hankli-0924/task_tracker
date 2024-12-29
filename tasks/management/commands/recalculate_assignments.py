from django.core.management.base import BaseCommand, CommandError
from tasks.models import TeamMember
from tasks.services.scheduling_service import recalculate_all_assignments_schedule

class Command(BaseCommand):
    help = 'Recalculate the schedules for all assignments of each team member'

    def add_arguments(self, parser):
        # Optional argument to specify a particular team member by ID
        parser.add_argument(
            '--team-member',
            type=int,
            help='ID of the team member whose assignments should be recalculated'
        )

    def handle(self, *args, **options):
        team_member_id = options['team_member']

        if team_member_id:
            try:
                team_member = TeamMember.objects.get(id=team_member_id)
                self.stdout.write(f'Recalculating assignments for team member {team_member}')
                recalculate_all_assignments_schedule(team_member)
                self.stdout.write(self.style.SUCCESS('Successfully recalculated assignments'))
            except TeamMember.DoesNotExist:
                raise CommandError(f'TeamMember with id {team_member_id} does not exist.')
        else:
            self.stdout.write('Recalculating assignments for all team members')
            for team_member in TeamMember.objects.all():
                recalculate_all_assignments_schedule(team_member)
                self.stdout.write(f'Successfully recalculated assignments for {team_member}')

            self.stdout.write(self.style.SUCCESS('All assignments have been successfully recalculated'))