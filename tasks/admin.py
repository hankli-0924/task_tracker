from django.contrib import admin
from .models import TeamMember, Task, Assignment

# Define an inline admin class for Assignment
class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 1  # Number of empty forms to display for adding new assignments
    autocomplete_fields = ['team_member']  # Optional: Use autocomplete for team members

# Define a custom admin class for Task
class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_name', 'priority', 'created_at', 'updated_at')
    search_fields = ('task_name',)
    list_filter = ('priority', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    inlines = [AssignmentInline]

# Define a custom admin class for TeamMember
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'position')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'department', 'position')
    list_filter = ('position', 'department')

# Define a custom admin class for Assignment
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('task', 'team_member', 'assigned_at', 'notes')
    search_fields = ('task__task_name', 'team_member__user__username')
    list_filter = ('assigned_at',)
    date_hierarchy = 'assigned_at'

# Register the models with their respective admin classes
admin.site.register(TeamMember, TeamMemberAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Assignment, AssignmentAdmin)