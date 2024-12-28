from django.db import models
from django.contrib.auth.models import User  # Assuming you're using Django's built-in User model for team members
from simple_history.models import HistoricalRecords


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


class WorkCalendar(models.Model):
    STATUS_CHOICES = [
        ('leave', 'Leave (Not Working)'),
        ('overtime', 'Overtime (Working)'),
        # ('weekend', 'Weekend (Not Working)'),
        # ('holiday', 'Public Holiday (Not Working)'),
    ]

    team_member = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='work_calendars')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    class Meta:
        # 确保一个团队成员在一天内只有一个状态
        unique_together = ('team_member', 'date')

    def __str__(self):
        return f'{self.team_member} - {self.date}: {self.get_status_display()}'


class Task(models.Model):
    TASK_NAME_MAX_LENGTH = 255
    PRIORITY_CHOICES = [
        ('P2', 'P2'),
        ('P1', 'P1'),
        ('P0', 'P0'),
    ]

    task_name = models.CharField(
        max_length=TASK_NAME_MAX_LENGTH,
        help_text="The name of the task."
    )
    description = models.TextField(default='', blank=True)

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='P1',
        help_text="The priority level of the task."
    )

    real_priority = models.IntegerField(
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

    workload = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="The estimated workload of the task in person-days (only for leaf tasks)."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Many-to-Many relationship with TeamMember through the Assignment model
    team_members = models.ManyToManyField(TeamMember, through='Assignment')

    history = HistoricalRecords()

    def __str__(self):
        return self.task_name

    class Meta:
        ordering = ['level', '-priority', 'created_at']

    @property
    def total_workload(self):
        """Calculate the total workload including all sub-tasks."""
        if self.sub_tasks.exists():
            return sum(task.total_workload for task in self.sub_tasks.all())
        else:
            return self.workload or 0


class TaskPredecessor(models.Model):
    from_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_predecessors')
    to_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_successors')
    established_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_task', 'to_task')


class Assignment(models.Model):
    """Intermediary model to manage assignments of team members to tasks."""
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
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
