from django.urls import path
from . import views

urlpatterns = [
    path('gantt-chart/', views.gantt_chart_view, name='gantt_chart'),
]