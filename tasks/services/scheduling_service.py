import logging

from django.db.models import Q
from django.db.models.aggregates import Max
from django.utils import timezone
from collections import deque, defaultdict
from tasks.models import Assignment, TaskPredecessor, WorkCalendar

logger = logging.getLogger('tasks')  # 使用特定的应用程序日志记录器


class ScheduleService:

    @staticmethod
    def get_dependency_order(tasks):
        """Determine the dependency order of tasks."""
        graph = defaultdict(list)
        in_degree = {task: 0 for task in tasks}

        for predecessor in TaskPredecessor.objects.filter(to_task__in=tasks):
            graph[predecessor.from_task].append(predecessor.to_task)
            in_degree[predecessor.to_task] += 1

        queue = deque([task for task in tasks if in_degree[task] == 0])
        ordered_tasks = []

        while queue:
            current_task = queue.popleft()
            ordered_tasks.append(current_task)

            for next_task in graph[current_task]:
                in_degree[next_task] -= 1
                if in_degree[next_task] == 0:
                    queue.append(next_task)

        if len(ordered_tasks) != len(tasks):
            raise ValueError("Cycle detected in task dependencies")

        return ordered_tasks

    @staticmethod
    def recalculate_assignment_schedule(assignment: Assignment):
        """Recalculate the schedule for a single assignment considering its dependencies and working calendar."""
        max_planned_end_time = \
            Assignment.objects.filter(team_member=assignment.team_member, need_update=False).aggregate(
                Max('planned_end_time'))['planned_end_time__max']

        max_actual_end_time = Assignment.objects.filter(team_member=assignment.team_member).aggregate(
            Max('actual_end_time'))['actual_end_time__max']

        new_planned_start_date_for_assignment = max(
            [end_time for end_time in [max_actual_end_time, max_planned_end_time, timezone.now()] if
             end_time is not None])

        # Use the team member's work calendar to find the next available workday
        start_date = WorkCalendar.get_next_available_workday(
            assignment.team_member,
            new_planned_start_date_for_assignment.date()
        )

        # Calculate the planned end time using the work calendar
        end_date = WorkCalendar.add_working_hours(
            assignment.team_member,
            start_date,
            float(assignment.effort_estimation or 0) * 8
        )

        assignment.planned_start_time = start_date
        assignment.planned_end_time = end_date
        assignment.need_update = False
        assignment.save()
        logger.info(
            f'Recalculated schedule for assignment {assignment}, estimation is {assignment.effort_estimation} new start_date is {start_date}, new end_date is {end_date}')

    @staticmethod
    def reschedule_team_member(team_member):
        """Reschedule all assignments for a specific team member considering dependency order."""
        Assignment.objects.filter(team_member=team_member,
                                  task__level=1,
                                  actual_start_time__isnull=True,
                                  actual_end_time__isnull=True).update(need_update=True)
        assignments = Assignment.objects.filter(
            team_member=team_member,
            task__level=1,
            actual_start_time__isnull=True,
            actual_end_time__isnull=True,
            effort_estimation__isnull=False
        ).select_related('task').order_by('task__level', 'task__priority', 'task__created_at')
        for assignment in assignments:
            ScheduleService.recalculate_assignment_schedule(assignment)
            logger.info(f'recalculate_assignment_schedule for {assignment} done')
