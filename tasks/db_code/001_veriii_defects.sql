drop view if exists veriii_defects CASCADE;
create view veriii_defects as
select content                                                                  as issue_description,
       "Executor"                                                               as owner,
--        "Update Time",
--        "Start Date",
--        "Due Date",
       问题类别                                                                 as type,
       系统名                                                                   as sys_name,
       模块                                                                     as module_name,
       "Priority"                                                               as priority,
       case "Priority"
           when '非常紧急' then 1
           when '紧急' then 2
           when '普通' then 3
           when '较低'
               then 4 end                                                       as priority_no,
       "Workflow Status"                                                        as workflow_status,
       to_date("Creation Time", 'yyyy-mm-dd')                                   as creation_time,
       extract(day from now() -
                        to_timestamp("Creation Time", 'yyyy-mm-dd hh24:mi:ss')) as days_since_creation,
       to_date("complete time", 'yyyy-mm-dd')                                   as complete_time
from all_veriii_defects
where "Workflow Status" not in
      ('Suspended[暂停]', 'Discarded[丢弃]', 'To Be Developed[待开发]', 'To Be Discussed(待讨论）');
-- order by priority_no, creation_time

--
--
-- Suspended[暂停]
-- Discarded[丢弃]
-- To Be Developed[待开发]
-- 待部署生产环境
-- Pending[待认领]
-- Verified(生产问题则代表已发版)
-- To Be Discussed(待讨论）
-- Working On It[工作进行中]
