from datetime import datetime, timedelta, time
from django.db import models
from django.contrib.auth.models import User  # Assuming you're using Django's built-in User model for team members
from django.utils import timezone
from simple_history.models import HistoricalRecords
from .veriii_defects import VeriiiDefects
from .veriiii_tasks import VeriiiTasks
class TeamMember(models.Model):
    POSITION_CHOICES = [
        ('frontend', 'Frontend Developer'),
        ('backend', 'Backend Developer'),
        ('ui_ux', 'UI/UX Designer'),
        ('test', 'Tester'),
        ('pm', 'Project manager or Production manager'),
    ]

    # 定义部门选择项
    DEPARTMENT_CHOICES = [
        ('tech_team', 'Tech Team'),  # 假设这是你想要添加的一个选项
        # 可以在这里添加更多选项
        # ('other_department', 'Other Department'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # department = models.CharField(max_length=100, blank=True, null=True)
    # 更新 department 字段，使用 choices 参数
    department = models.CharField(
        max_length=100,
        choices=DEPARTMENT_CHOICES,  # 使用定义的选择项
        blank=True,
        null=True,
        default=None,  # 如果有默认值可以指定，默认为 None 表示没有默认值
    )
    position = models.CharField(
        max_length=20,
        choices=POSITION_CHOICES,
        default='frontend',
        help_text="The role of the team member."
    )
    history = HistoricalRecords()

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Holiday(models.Model):
    """Model to store public holidays that apply to all team members."""
    date = models.DateField(unique=True)
    name = models.CharField(max_length=100, help_text="Name of the holiday")

    def __str__(self):
        return f'{self.name} on {self.date}'


class WorkCalendar(models.Model):
    """Though this is named work calendar. Not all working days are stored in this model ,
    only special days(working overtime or taking personal leave) are maintained in this table,
    and the final actual working days are calculated based on special days maintained in this model for each individual."""
    STATUS_CHOICES = [
        ('leave', 'Leave (Not Working)'),
        ('overtime', 'Overtime (Working)'),
    ]

    team_member = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='work_calendars')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    '''This can be used for either working over time or for a regular working day , as 
    any record in this table will be considered first'''
    hours_worked = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True,
                                       help_text="Actual hours worked on this day")

    class Meta:
        unique_together = ('team_member', 'date')

    def __str__(self):
        return f'{self.team_member} - {self.date}: {self.get_status_display()}, Hours Worked: {self.hours_worked or "N/A"}'

    @classmethod
    def is_working_day(cls, team_member, date):
        """Check if the given date is a working day for the specified team member."""
        try:
            entry = cls.objects.get(team_member=team_member, date=date)
            return entry.status == 'overtime'
        except cls.DoesNotExist:
            pass  # Proceed with further checks if no specific entry exists

        if date.weekday() >= 5 or Holiday.objects.filter(date=date).exists():
            return False

        return True

    @classmethod
    def get_next_available_workday(cls, team_member, start_date):
        """Find the next available workday starting from the given date for the specified team member."""
        date_to_check = start_date
        work_start_time = time(9, 0, 0)  # 工作开始时间为上午9:00
        while True:
            if cls.is_working_day(team_member, date_to_check):
                return timezone.make_aware(datetime.combine(date_to_check, work_start_time))
            date_to_check += timedelta(days=1)

    @classmethod
    def get_daily_working_hours(cls, team_member, date):
        """Get the number of working hours on a given date for the specified team member."""
        try:
            entry = cls.objects.get(team_member=team_member, date=date)
            return entry.hours_worked or 8  # Assuming 8 hours as the default working day
        except cls.DoesNotExist:
            return 8  # Default working hours if no special entry exists

    @classmethod
    def get_end_of_working_day(cls, team_member, date):
        """Get the end of the working day for a given date for the specified team member."""
        try:
            entry = cls.objects.get(team_member=team_member, date=date)
            if entry.status == 'overtime':
                return timezone.make_aware(datetime.combine(date, time(hour=23, minute=59)))
            else:
                return timezone.make_aware(
                    datetime.combine(date, time(hour=17, minute=0)))  # Assuming standard end time
        except cls.DoesNotExist:
            return timezone.make_aware(datetime.combine(date, time(hour=17, minute=0)))  # Standard end time by default

    @classmethod
    def add_working_hours(cls, team_member, start_date, hours_to_add):
        """Add working hours to a date using the given team member's calendar."""
        end_date = start_date
        accumulated_hours = 0

        while accumulated_hours < hours_to_add:
            if cls.is_working_day(team_member, end_date.date()):
                daily_hours = cls.get_daily_working_hours(team_member, end_date.date())
                remaining_hours = hours_to_add - float(accumulated_hours)
                if daily_hours >= remaining_hours:
                    end_date += timedelta(hours=remaining_hours)
                    break
                else:
                    accumulated_hours += daily_hours
                    end_date += timedelta(days=1)
            else:
                end_date += timedelta(days=1)

        # Ensure end_date is at the end of the working day
        end_date = cls.get_end_of_working_day(team_member, end_date.date())

        return end_date


class Task(models.Model):
    """Definition of task is from product point of view, actual task assignment is handled by model Assignment.
    Sometimes the difference between Task and Assignment can be subtle, as one task can have multiple assignments.
    Task can also have multiple sub-tasks.
    So, when inserting data into Task ,please also think from product/function point of view, don't think too much
    about the actual assignment of the task.
    """
    TASK_NAME_MAX_LENGTH = 255

    task_name = models.CharField(
        max_length=TASK_NAME_MAX_LENGTH,
        help_text="The name of the task."
    )
    description = models.TextField(default='', blank=True)

    priority = models.IntegerField(
        default=0,
        help_text="The priority level of the task within its level."
    )

    level = models.IntegerField(
        default=1,
        help_text="The level of the task in the hierarchy."
    )

    parent_task = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='sub_tasks',
        help_text="The parent task this task belongs to."
    )

    # And then modify the Task model to use this through model
    predecessors = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        through='TaskPredecessor',
        related_name='successors'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Many-to-Many relationship with TeamMember through the Assignment model
    team_members = models.ManyToManyField(TeamMember, through='Assignment')

    history = HistoricalRecords()

    def __str__(self):
        return self.task_name

    class Meta:
        ordering = ['level',
                    # 'priority',
                    'created_at']

    @property
    def total_effort_estimation(self):
        """Calculate the total effort estimation including all sub-tasks."""
        if self.sub_tasks.exists():
            # For parent tasks, sum up the effort estimations of all sub-tasks
            return sum(task.total_effort_estimation for task in self.sub_tasks.all())
        else:
            # For leaf tasks, sum up the effort estimations from assignments
            return sum(assignment.effort_estimation or 0 for assignment in self.assignments.all())


class TaskPredecessor(models.Model):
    from_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_predecessors')
    to_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_successors')
    established_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_task', 'to_task')


class Assignment(models.Model):
    """Intermediary model to manage assignments of team members to tasks."""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='assignments')
    team_member = models.ForeignKey(TeamMember, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    # Fields for Gantt chart data
    effort_estimation = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                            help_text="Estimated effort in man days")
    planned_start_time = models.DateTimeField(null=True, blank=True)
    planned_end_time = models.DateTimeField(null=True, blank=True)
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    need_update = models.BooleanField(default=False, help_text='Need update?')

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.task.task_name} assigned to {self.team_member}"
