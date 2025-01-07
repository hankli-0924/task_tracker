from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from django.utils import timezone
from datetime import timedelta, date
from .models import TeamMember, Task, Assignment, TaskPredecessor, Holiday, WorkCalendar, VeriiiDefects, VeriiiTasks, \
    AllCompletionWork


class LastMonthFilter(admin.SimpleListFilter):
    title = 'planed end time'
    parameter_name = 'planed_end_time'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('last_month', 'Last month'),
            ('this_month', 'This month'),
            ('this_year', 'This year'),
            ('past_7_days', 'Past 7 days'),
            ('today', 'Today'),
            ('any_date', 'Any date'),
            ('no_date', 'No date'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        now = timezone.now()
        if self.value() == 'last_month':
            # Calculate the start and end of last month
            this_month_start = date(now.year, now.month, 1)
            last_month_end = this_month_start - timedelta(days=1)
            last_month_start = date(last_month_end.year, last_month_end.month, 1)
            return queryset.filter(planed_end_time__gte=last_month_start, planed_end_time__lte=last_month_end)
        elif self.value() == 'this_month':
            this_month_start = date(now.year, now.month, 1)
            next_month = this_month_start.replace(day=28) + timedelta(days=4)  # this will never fail
            this_month_end = next_month - timedelta(days=next_month.day)
            return queryset.filter(planed_end_time__gte=this_month_start, planed_end_time__lte=this_month_end)
        elif self.value() == 'this_year':
            this_year_start = date(now.year, 1, 1)
            this_year_end = date(now.year, 12, 31)
            return queryset.filter(planed_end_time__gte=this_year_start, planed_end_time__lte=this_year_end)
        elif self.value() == 'past_7_days':
            seven_days_ago = now - timedelta(days=7)
            return queryset.filter(planed_end_time__gte=seven_days_ago)
        elif self.value() == 'today':
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            return queryset.filter(planed_end_time__gte=today_start, planed_end_time__lte=today_end)
        elif self.value() == 'any_date':
            return queryset.exclude(planed_end_time__isnull=True)
        elif self.value() == 'no_date':
            return queryset.filter(planed_end_time__isnull=True)


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
        'task', 'team_member', 'effort_estimation', 'planned_start_time', 'planned_end_time', 'actual_start_time',
        'actual_end_time', 'notes', 'assigned_at')
    search_fields = ('task__task_name', 'team_member__user__username')
    list_filter = ('planned_end_time', 'team_member', 'task__level', 'task__priority', 'task__task_name', 'need_update')
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


@admin.register(VeriiiDefects)
class VeriiiDefectsAdmin(admin.ModelAdmin):
    list_display = (
        'issue_description', 'owner', 'type', 'sys_name', 'module_name', 'priority','priority_no', 'workflow_status',
        'creation_time', 'days_since_creation')
    list_filter = ('owner', 'workflow_status', 'priority', 'creation_time')  # Add fields you want to filter by
    search_fields = ('issue_description', 'owner', 'sys_name', 'module_name')  # Add fields you want to be searchable
    date_hierarchy = 'creation_time'  # Optional: adds date-based drill-down navigation
    ordering = ('priority_no', 'creation_time',)  # Sorts records when they appear in the admin


@admin.register(VeriiiTasks)
class VeriiiTasksAdmin(admin.ModelAdmin):
    # 自定义管理界面显示哪些字段
    list_display = (
        'task_name',
        'priority',
        'username',
        'planed_start_time',
        'planed_end_time',
        'effort_estimation_in_man_days',
        'actual_start_time',
        'actual_end_time')

    # 添加搜索框，指定可搜索的字段
    search_fields = ['task_name', 'username']

    # 添加过滤器
    list_filter = ('priority', 'planed_start_time', LastMonthFilter)

    # 指定默认排序字段，负号表示降序
    ordering = ('-planed_start_time',)

    # 如果有外键字段，可以使用 raw_id_fields 提高编辑效率
    # raw_id_fields = ('some_foreign_key_field',)

    # 如果有大量数据，分页显示
    list_per_page = 20

    # 只读字段
    readonly_fields = ('planned_verification_time',)

    # 添加 date_hierarchy 支持
    # date_hierarchy = 'planed_end_time'



class CompleteTimeLastMonthFilter(admin.SimpleListFilter):
    title = 'complete time'
    parameter_name = 'complete_time'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('last_month', 'Last month'),
            ('this_month', 'This month'),
            ('this_year', 'This year'),
            ('past_7_days', 'Past 7 days'),
            ('today', 'Today'),
            ('any_date', 'Any date'),
            ('no_date', 'No date'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        now = timezone.now()
        if self.value() == 'last_month':
            # Calculate the start and end of last month
            this_month_start = date(now.year, now.month, 1)
            last_month_end = this_month_start - timedelta(days=1)
            last_month_start = date(last_month_end.year, last_month_end.month, 1)
            return queryset.filter(complete_time__gte=last_month_start, complete_time__lte=last_month_end)
        elif self.value() == 'this_month':
            this_month_start = date(now.year, now.month, 1)
            next_month = this_month_start.replace(day=28) + timedelta(days=4)  # this will never fail
            this_month_end = next_month - timedelta(days=next_month.day)
            return queryset.filter(complete_time__gte=this_month_start, complete_time__lte=this_month_end)
        elif self.value() == 'this_year':
            this_year_start = date(now.year, 1, 1)
            this_year_end = date(now.year, 12, 31)
            return queryset.filter(complete_time__gte=this_year_start, complete_time__lte=this_year_end)
        elif self.value() == 'past_7_days':
            seven_days_ago = now - timedelta(days=7)
            return queryset.filter(complete_time__gte=seven_days_ago)
        elif self.value() == 'today':
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            return queryset.filter(complete_time__gte=today_start, complete_time__lte=today_end)
        elif self.value() == 'any_date':
            return queryset.exclude(complete_time__isnull=True)
        elif self.value() == 'no_date':
            return queryset.filter(complete_time__isnull=True)


@admin.register(AllCompletionWork)
class AllCompletionWorkAdmin(admin.ModelAdmin):
    list_display = ('task_type', 'issue_description', 'owner', 'complete_time', 'days_spent')
    search_fields = ('task_type', 'issue_description', 'owner')
    list_filter = ('task_type', 'owner', CompleteTimeLastMonthFilter)
    date_hierarchy = 'complete_time'
    ordering = ('-complete_time',)


# Register the models with their respective admin classes
admin.site.register(TeamMember, TeamMemberAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Holiday, HolidayAdmin)
admin.site.register(WorkCalendar, WorkCalendarAdmin)
admin.site.register(TaskPredecessor)
