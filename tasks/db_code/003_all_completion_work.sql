drop view if exists all_completion_work CASCADE;
create view all_completion_work as
select 'issues'                                                    as task_type,
       issue_description,
       case owner when '牧野' then '李治文' else owner end         as owner,
       veriii_defects.complete_time,
       DATE_TRUNC('month', veriii_defects.complete_time)           as completion_month,
       veriii_defects.complete_time - veriii_defects.creation_time as days_spent
from veriii_defects
where veriii_defects.complete_time is not null
  and workflow_status = 'Closed'
union all

select 'tasks',
       task_name,
       username,
       veriii_tasks.actual_end_time,
       DATE_TRUNC('month', veriii_tasks.actual_end_time) as completion_month,
       veriii_tasks.effort_estimation_in_man_days
from veriii_tasks
where actual_end_time is not null;
