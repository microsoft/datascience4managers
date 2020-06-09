# This is just a script for managing the database, it is not part of the app.

# res = ['rec.unicycles', 'Corker, Nimbus, UMX', 'alt.astrology', 'Libra, Scorpio, Gemini']

import pandas as pd
import sqlite3

DB_NAME = 'app_db.sqlite3'

TRAINING_DATA = 'NewsgroupSampler/data/train_clean.tsv'
newsgroup_data = pd.read_table(TRAINING_DATA)


con = sqlite3.connect(DB_NAME) # ':memory:')
cur = con.cursor()
cur.execute("create table if not exists newsgroup_msg(key int, newsgroup text, msg text)")

insert_sql = "insert into newsgroup_msg(key, newsgroup, msg) values (?,?,?)"

for index, row in newsgroup_data.iterrows():
    record = [index, row['label'], row['msg']]
    # print(*record, '\n')
    cur.execute(insert_sql, record)

con.commit()
con.close()

def get_random_pair_of_posts():
    rpp_query = """ with newsgroups as (select distinct newsgroup from newsgroup_msg),
        ng_pair as (select newsgroup from newsgroups order by random() limit 2),
        post1 as (select newsgroup_msg.* from newsgroup_msg join ng_pair 
                    on newsgroup_msg.newsgroup=ng_pair.newsgroup 
                    order by random() limit 1),
        post2 as (select newsgroup_msg.* from newsgroup_msg join ng_pair 
                    on newsgroup_msg.newsgroup=ng_pair.newsgroup 
                    join post1 on ng_pair.newsgroup != post1.newsgroup
                    order by random() limit 1)
        select newsgroup, msg from post1
            union 
        select newsgroup, msg from post2;
    """
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute(rpp_query)
    rpp = []
    for row in cur.fetchall():
        rpp.append(row)
    con.close()
    return [{'newsgroup':rpp[0][0], 'msg':rpp[0][1]}, {'newsgroup':rpp[1][0], 'msg':rpp[1][1]}]





    
    
    newsgroup_msg where newsgroup in 
        ;