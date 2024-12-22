from django.shortcuts import render
import plotly.graph_objs as go
from .models import Assignment


def gantt_chart_view(request):
    assignments = Assignment.objects.all()

    fig = go.Figure()

    for assignment in assignments:
        fig.add_trace(go.Bar(
            x=[(
                       assignment.planned_end_time - assignment.planned_start_time).total_seconds() / 3600 if assignment.planned_start_time and assignment.planned_end_time else None],
            y=[assignment.task.task_name],
            base=[assignment.planned_start_time.timestamp() * 1000 if assignment.planned_start_time else None],
            orientation='h',
            name=f"Planned ({assignment.team_member})"
        ))

        if assignment.actual_start_time and assignment.actual_end_time:
            fig.add_trace(go.Bar(
                x=[(assignment.actual_end_time - assignment.actual_start_time).total_seconds() / 3600],
                y=[assignment.task.task_name],
                base=[assignment.actual_start_time.timestamp() * 1000],
                orientation='h',
                name=f"Actual ({assignment.team_member})",
                opacity=0.6
            ))

    fig.update_layout(
        title='Task Assignments Gantt Chart',
        barmode='overlay',
        xaxis_title="Time (Hours)",
        yaxis_title="Tasks"
    )

    chart_html = fig.to_html(full_html=False)

    return render(request, 'gantt_chart.html', {'chart_html': chart_html})
