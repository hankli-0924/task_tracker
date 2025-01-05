drop view if exists veriii_tasks;
create view veriii_tasks as
select tasks_assignment.id,
       tasks_task.task_name                      as task_name,
       'P' || tasks_task.priority                as priority,
       au.username,
       tasks_assignment.planned_start_time::date as planed_start_time,
       tasks_assignment.planned_end_time::date   as planed_end_time,
       (tasks_assignment.planned_end_time +
        INTERVAL '1 hour' * (tasks_assignment.effort_estimation * 0.33 * 8)::int)::date
                                                 as planned_verification_time,
       tasks_assignment.effort_estimation           effort_estimation_in_man_days,
       tasks_assignment.actual_start_time::date  as actual_start_time,
       tasks_assignment.actual_end_time::date    as actual_end_time
from tasks_assignment
         join tasks_teammember tt on tasks_assignment.team_member_id = tt.id
         join auth_user au on tt.user_id = au.id
         join tasks_task on tasks_assignment.task_id = tasks_task.id;
-- where tasks_assignment.actual_end_time is null
-- order by tasks_task.priority, tasks_assignment.planned_start_time, tasks_assignment.planned_end_time;
