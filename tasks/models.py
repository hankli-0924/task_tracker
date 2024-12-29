from datetime import datetime, timedelta, time
from django.db import models
from django.contrib.auth.models import User  # Assuming you're using Django's built-in User model for team members
from django.utils import timezone
from simple_history.models import HistoricalRecords

from tasks.utils import get_today


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

    @staticmethod
    def is_working_day(team_member, date):
        """Check if the given date is a working day for the specified team member."""
        # First check if there's an entry in WorkCalendar for this date and team member
        try:
            entry = WorkCalendar.objects.get(team_member=team_member, date=date)
            # If it's marked as overtime, consider it a working day regardless of other conditions
            # return False is team member takes leave on that very day
            return entry.status == 'overtime'
        except WorkCalendar.DoesNotExist:
            pass  # Proceed with further checks if no specific entry exists

        # Check if the date is a weekend or a public holiday
        if date.weekday() >= 5:  # Saturday (5) and Sunday (6)
            return False
        if Holiday.objects.filter(date=date).exists():
            return False

        # If there's no entry and it's not a weekend or holiday, assume it's a working day by default
        return True

    @classmethod
    def get_next_available_workday(cls, team_member, start_date):
        """Find the next available workday starting from the given date for the specified team member."""
        date_to_check = start_date
        while True:
            if cls.is_working_day(team_member, date_to_check):
                return timezone.make_aware(datetime.combine(date_to_check, time.min))
            date_to_check += timedelta(days=1)


class Task(models.Model):
    """Definition of task is from product point of view, actual task assignment is handled by model Assignment.
    Sometimes the difference between Task and Assignment can be subtle, as one task can have multiple assignments.
    Task can also have multiple sub-tasks.
    So, when inserting data into Task ,please also think from product/function point of view, don't think too much
    about the actual assignment of the task.
    """
    TASK_NAME_MAX_LENGTH = 255
    # PRIORITY_CHOICES = [
    #     ('P2', 'P2'),
    #     ('P1', 'P1'),
    #     ('P0', 'P0'),
    # ]

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
                                            help_text="Estimated effort in hours")
    planned_start_time = models.DateTimeField(null=True, blank=True)
    planned_end_time = models.DateTimeField(null=True, blank=True)
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.task.task_name} assigned to {self.team_member}"
