from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import TeamMember, Task, Assignment, TaskPredecessor, Holiday, WorkCalendar


# Define an inline admin class for Assignment
class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 1  # Number of empty forms to display for adding new assignments
    autocomplete_fields = ['team_member']  # Optional: Use autocomplete for team members


class TaskPredecessorInline(admin.TabularInline):
    model = TaskPredecessor
    fk_name = 'from_task'  # 因为TaskPredecessor有两个外键指向Task，所以需要指定哪个是"父"键
    extra = 1


# Define a custom admin class for Task
class TaskAdmin(SimpleHistoryAdmin):
    list_display = ('task_name', 'priority', 'level', 'parent_task', 'created_at', 'updated_at')
    search_fields = ('task_name',)
    list_filter = ('level', 'priority', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    inlines = [AssignmentInline, TaskPredecessorInline]
    # filter_horizontal = ('predecessors',)  # 更方便地选择前置任务

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('assignments', 'sub_tasks')  # 提高查询效率


# Define a custom admin class for TeamMember
class TeamMemberAdmin(SimpleHistoryAdmin):
    list_display = ('user', 'department', 'position')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'department', 'position')
    list_filter = ('position', 'department')


# Define a custom admin class for Assignment
class AssignmentAdmin(SimpleHistoryAdmin):
    list_display = (
        'task', 'team_member', 'planned_start_time', 'planned_end_time', 'actual_end_time', 'notes', 'assigned_at')
    search_fields = ('task__task_name', 'team_member__user__username')
    list_filter = ('assigned_at', 'team_member', 'task__level', 'task__priority')
    date_hierarchy = 'assigned_at'


# Define a custom admin class for Holiday
class HolidayAdmin(SimpleHistoryAdmin):
    list_display = ('date', 'name')
    search_fields = ('name',)
    date_hierarchy = 'date'


# Define a custom admin class for WorkCalendar
class WorkCalendarAdmin(SimpleHistoryAdmin):
    list_display = ('team_member', 'date', 'status', 'hours_worked')
    list_filter = ('status', 'team_member__department', 'team_member__position')
    date_hierarchy = 'date'
    search_fields = ('team_member__user__username',)


# Register the models with their respective admin classes
# Register the models with their respective admin classes
admin.site.register(TeamMember, TeamMemberAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Holiday, HolidayAdmin)
admin.site.register(WorkCalendar, WorkCalendarAdmin)
admin.site.register(TaskPredecessor)