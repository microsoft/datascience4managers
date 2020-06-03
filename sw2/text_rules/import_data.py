# This is just a script for managing the database, it is not part of the app.

# res = ['rec.unicycles', 'Corker, Nimbus, UMX', 'alt.astrology', 'Libra, Scorpio, Gemini']

import pandas as pd
import sqlite3
import psycopg2
from SECRETS import SECRETS

DBMS = 'SQLite' # Postgress
DB_NAME = 'app_db.sqlite3'

TRAINING_DATA = r'C:\Users\rhorton\Documents\conferences\MLADS\MLADS_fall_2019\part_1_JMA\text_classification_data\train_clean.tsv'
newsgroup_data = pd.read_table(TRAINING_DATA)

if DBMS == "SQLite":
	con = sqlite3.connect(DB_NAME) # ':memory:')
	insert_sql = "insert into newsgroup_msg(key, newsgroup, msg) values (?,?,?)
else:
	con = psycopg2.connect(dbname='postgres', 
							user='demoadmin@marinchpg1',
							host ='marinchpg1.postgres.database.azure.com', 
							password='marinchBoBdb1', port='5432')
	insert_sql = "insert into newsgroup_msg(key, newsgroup, msg) values (%s,%s,%s)"

cur = con.cursor()
cur.execute("create table if not exists newsgroup_msg(key int, newsgroup text, msg text)")



for index, row in newsgroup_data.iterrows():
	if DBMS == "SQLite":
		record = [index, row['label'], row['msg']]
	else:
		record = (index, row['label'], row['msg'])
	# print(*record, '\n')
	cur.execute(insert_sql, record)


con.commit()
con.close()






db = psycopg2.connect(dbname=SECRETS['dbname'], user=SECRETS['user'], host =SECRETS['host'], password=SECRETS['password'], port=SECRETS['port'])

get_random_pair_of_posts(db)

db.close()

def initialize_results_table(con):
	CREATE_TABLE_SQL = """CREATE TABLE IF NOT EXISTS 
		newsgroup_term(
			newsgroup TEXT, 
			term TEXT, 
			created_at TIMESTAMP DEFAULT NOW())"""
	cur = con.cursor()
	cur.execute(CREATE_TABLE_SQL)
	con.commit()


def upload_results_from_sqlite(in_con, out_con):
	in_query = """select newsgroup, term from newsgroup_term"""
	out_query = """insert into newsgroup_term(newsgroup, term) values (%s,%s)"""
	in_cursor = in_con.cursor()
	out_cursor = out_con.cursor()
	in_cursor.execute(in_query)
	row = in_cursor.fetchone()
	while row is not None:
		rec = (row[0], row[1])
		print("{} : {}".format(*rec))
		out_cursor.execute(out_query, rec)
		row = in_cursor.fetchone()
	in_con.commit()
	out_con.commit()


local_db = sqlite3.connect(DB_NAME)

upload_results_from_sqlite(local_db, db)
