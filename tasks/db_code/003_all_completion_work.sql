drop view if exists all_completion_work CASCADE;
drop view if exists all_completion_tasks CASCADE;
create view all_completion_work as
select 'issues'                                                    as task_type,
       issue_description,
       case owner when '牧野' then '李治文' else owner end         as owner,
       veriii_defects.complete_time,
       veriii_defects.complete_time - veriii_defects.creation_time as days_spent
from veriii_defects
where veriii_defects.complete_time is not null

union all

select 'tasks', task_name, username, veriii_tasks.actual_end_time, veriii_tasks.effort_estimation_in_man_days
from veriii_tasks
where actual_end_time is not null;
