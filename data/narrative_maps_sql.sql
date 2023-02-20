#truncate table_experiment;
#truncate table_run;
#truncate table_parsed_text;


select * from table_experiment;
select * from table_run;
select * from table_parsed_text;
select * from table_generate_params;
select * from table_embedding_params;

update table_parsed_text set cluster_name = 'no _clstr' where cluster_id = -1;


select MAX(run_id) as max from table_run where experiment_id = 1;

create or replace view parsed_view as
select tr.experiment_id, tr.id as run_index, pt.*, ep.model as embedding_model
from table_parsed_text pt
         inner join table_run tr on pt.run_id = tr.id
         inner join table_embedding_params ep on tr.embedding_params = ep.id;

select * from parsed_view;

select experiment_id, id, parsed_text, embedding_model, embedding from parsed_view where embedding IS NOT NULL;

create or replace view run_parsed_view as
select r.experiment_id, r.id, r.run_id, r.prompt, r.response, gp.model as generate_model, ep.model as embedding_model, pt.id as line_index, pt.parsed_text
from table_run r
         inner join table_parsed_text pt on r.id = pt.run_id
         inner join table_generate_params gp on r.generator_params = gp.id
         inner join table_embedding_params ep on r.embedding_params = ep.id;

select * from run_parsed_view;

create or replace view run_params_view as
select r.experiment_id, r.id, r.run_id, r.prompt, r.response, gp.model as generate_model, gp.tokens, gp.presence_penalty,
       gp.frequency_penalty, ep.model as embedding_model, ep.PCA_dim, ep.EPS, ep.min_samples, ep.perplexity
from table_run r
         inner join table_generate_params gp on r.generator_params = gp.id
         inner join table_embedding_params ep on r.generator_params = ep.id;
select * from run_params_view;

create or replace view index_view as
select e.id as experiment_id, r.id as run_id, p.id as parsed_text_id, g.id as gen_id, ep.id as emb_id
from table_experiment e
         inner join table_run r on e.id = r.experiment_id
         inner join table_parsed_text p on r.run_id = p.run_id
         inner join table_generate_params g on r.embedding_params = g.id
         inner join table_embedding_params ep on r.embedding_params;

select * from index_view;
select distinct emb_id from index_view where experiment_id = 1;
select distinct parsed_text_id from index_view where experiment_id = 1;



