#truncate table_parsed_text;
truncate table_summary_text;
update table_parsed_text set summary_id = NULL where summary_id IS NOT NULL;

select * from table_parsed_text limit 110;
select * from table_parsed_text where id = 59;
select * from table_summary_text;

select distinct embedding from table_parsed_text;

select parsed_text, embedding from table_parsed_text limit 10;

select * from table_source;

create or replace view source_text_view as
select s.id as source_id, s.text_name, s.group_name, p.id as text_id, p.summary_id, p.parsed_text, p.embedding
from table_source s
         inner join table_parsed_text p on source = s.id;

select * from source_text_view limit 200;

create or replace view summary_text_view as
select ts.id as proj_id, ts.text_name, ts.group_name,
       tst.id as text_id, tst.summary_id, tst.level, tst.summary_text as parsed_text, tst.embedding, tst.origins
from table_summary_text tst
         inner join table_source ts on tst.source = ts.id;

select * from summary_text_view;