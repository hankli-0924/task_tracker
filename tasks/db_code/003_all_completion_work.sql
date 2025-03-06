drop view if exists all_completion_work CASCADE;
create view all_completion_work as
select 'defect' || id::text                                        as id,
       'issues'                                                    as task_type,
       issue_description                                           as description,
       case owner when '牧野' then '李治文' else owner end         as owner,
       veriii_defects.complete_time,
       to_char(veriii_defects.complete_time, 'YYYY-MM')            as completion_month,
       veriii_defects.complete_time - veriii_defects.creation_time as days_spent,
       '' as note
from veriii_defects
where veriii_defects.complete_time is not null
  and workflow_status = 'Closed'
union all

select 'task' || veriii_task_assignments.id::text,
       'tasks',
       veriii_task_assignments.task_name,
       username,
       veriii_task_assignments.actual_end_time,
       to_char(veriii_task_assignments.actual_end_time, 'YYYY-MM')                                         as completion_month,

--        veriii_task_assignments.effort_estimation_in_man_days
       veriii_task_assignments.actual_end_time::date + 1 - veriii_task_assignments.actual_start_time::date as days_spent,
       tasks_task.description
from veriii_task_assignments
join tasks_task on veriii_task_assignments.task_id=tasks_task.id
where actual_end_time is not null;
