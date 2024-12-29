from tasks.models import Assignment, WorkCalendar
from tasks.utils import get_today
from datetime import timedelta
from django.db.models import Q


def recalculate_all_assignments_schedule(team_member):
    """Recalculate the schedules for all assignments of a team member without considering conflicts."""

    # Fetch all assignments for the team member, ordered by task level and priority
    assignments = Assignment.objects.filter(
        team_member=team_member
    ).select_related('task').order_by('task__level', 'task__priority', 'task__created_at')

    current_date = get_today()

    for assignment in assignments:
        if assignment.effort_estimation is not None:
            working_hours_per_day = 8  # Assuming a standard 8-hour workday
            total_hours_needed = assignment.effort_estimation
            hours_counted = 0

            # Reset planned start time to the next available workday for each assignment
            planned_start_time = WorkCalendar.get_next_available_workday(team_member, current_date)

            # Initialize planned_end_time with planned_start_time
            planned_end_time = planned_start_time

            while hours_counted < total_hours_needed:
                if WorkCalendar.is_working_day(team_member, planned_end_time.date()):
                    # Only consider days marked as overtime or default working day with no leave
                    daily_work_entry = (
                        WorkCalendar.objects
                        .filter(
                            Q(team_member=team_member) &
                            Q(date=planned_end_time.date()) &
                            Q(status='overtime')
                        )
                        .first()
                    )

                    if daily_work_entry and daily_work_entry.hours_worked:
                        # If there's an overtime entry, use its hours_worked value
                        hours_worked_today = daily_work_entry.hours_worked
                    else:
                        # Otherwise, assume a standard working day with 8 hours
                        hours_worked_today = working_hours_per_day

                    hours_to_add = min(hours_worked_today, total_hours_needed - hours_counted)
                    hours_counted += hours_to_add

                    # Increment planned_end_time only after adding hours for the day
                    planned_end_time += timedelta(days=1)

            # Ensure the end time is a valid working day
            while not WorkCalendar.is_working_day(team_member, planned_end_time.date()):
                planned_end_time += timedelta(days=1)

            assignment.planned_start_time = planned_start_time
            assignment.planned_end_time = planned_end_time
            assignment.save()

            # Move planned_end_time forward for the next assignment
            current_date = planned_end_time  # Update current_date for the next iteration
