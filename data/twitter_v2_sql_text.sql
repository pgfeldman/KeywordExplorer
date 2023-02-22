mysqldump -u root -p --no-data twitter_v2 > twitter_v2_schema.sql

select * from table_experiment;
select * from table_query;
select * from table_tweet limit 10;
select * from table_exclude;
select * from table_user;

truncate table_experiment;
truncate table_query;
truncate table_tweet;
truncate table_exclude;
truncate table_user;

create or replace view keyword_tweet_view as
    select te.name, te.id as experiment_id, te.sample_start as start, te.sample_end as end, te.keywords,
           tq.query, tq.keyword,
           tt.author_id, tt.conversation_id, tt.id as tweet_id, tt.row_id as tweet_row, tt.text,
           tt.cluster_id, tt.cluster_name, tt.reduced, tt.is_thread, tt.embedding
    from table_experiment te
    inner join table_query tq on te.id = tq.experiment_id
    inner join table_tweet tt on tq.id = tt.query_id;

create or replace view tweet_user_cluster_view as
select te.id as experiment_id,
        tq.keyword,
        tt.text, tt.created_at, tt.lang, tt.cluster_id, if(tt.cluster_id = tex.cluster_id, TRUE, FALSE) as exclude,
        tu.name, tu.username, tu.location, tu.description

    from table_experiment te
    inner join table_query tq on te.id = tq.experiment_id
    inner join table_tweet tt on tq.id = tt.query_id
    inner join table_user tu on tu.id = tt.author_id
    left join table_exclude tex on tt.cluster_id = tex.cluster_id;

select * from keyword_tweet_view limit 10;
select name, keyword, text from keyword_tweet_view limit 10;
select name, keyword, text, conversation_id from keyword_tweet_view;
select distinct keyword, tweet_id, conversation_id from keyword_tweet_view where tweet_id != conversation_id and experiment_id = 1 and is_thread = FALSE;
select count(*) from keyword_tweet_view where is_thread = TRUE and experiment_id = 1;
select keyword, count(*) from keyword_tweet_view group by keyword;
select keyword, count(*) from keyword_tweet_view where experiment_id = 1 and is_thread = TRUE group by keyword;
select keyword, count(*) from keyword_tweet_view where experiment_id = 1 and conversation_id is not null and is_thread = FALSE group by keyword;
select keyword, count(*) from table_query where experiment_id  group by keyword;
select * from table_tweet;

select text from keyword_tweet_view where keyword = 'ivermectin';
select * from table_query where keyword like('ivermectin');
update table_query set experiment_id = 1 where experiment_id = -1;

select query_id, keyword, count(*) from table_tweet tt inner join table_query tq on tt.query_id = tq.id group by query_id;

select count(*) from table_tweet where embedding is null;
select tweet_id, embedding from keyword_tweet_view where experiment_id = 1 and keyword = 'paxlovid OR Nirmatrelvir OR ritonavir' LIMIT 10;

INSERT INTO table_exclude (cluster_id, experiment_id, keyword) VALUES (19, 1, 'paxlovid OR Nirmatrelvir OR ritonavir');
select count(*) from table_exclude where cluster_id = 19 and experiment_id = 1 and keyword = 'paxlovid OR Nirmatrelvir OR ritonavir';

select distinct author_id from table_tweet order by author_id;
select distinct author_id from keyword_tweet_view order by author_id;
replace into table_user (id, created_at, description, location, name, username, verified)
    VALUES (1289933022901370880, '2020-08-02 14:37:20', '\ud83c\uddfa\ud83c\udde6 \ud83d\udc97 #writer, proud parent of neurodivergent, gay, nonbinary beauties; poet, #mecfs (#pwME 30 years), chronic illness, #pointillism, #art, #politics',
            'North Carolina', 'J. Ruth Kelly (she/her)', 'something else', FALSE);

-------------------------------------------------------- gpt_experiments
select * from table_experiment;
select * from table_text;
select * from table_text_data;

create or replace view test_view as
    select tt.*, ttd_k.value as keyword, ttd_c.value as created, ttd_l.value as location, ttd_p.value as probability
    FROM table_text tt
    inner join table_text_data ttd_c on tt.id = ttd_c.text_id and ttd_c.name = 'created'
    inner join table_text_data ttd_k on tt.id = ttd_k.text_id and ttd_k.name = 'keyword'
    inner join table_text_data ttd_l on tt.id = ttd_l.text_id and ttd_l.name = 'location'
    inner join table_text_data ttd_p on tt.id = ttd_p.text_id and ttd_p.name = 'probability';

select * from test_view;


