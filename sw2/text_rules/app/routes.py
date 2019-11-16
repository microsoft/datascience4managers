from flask import render_template, flash, redirect, url_for, Response
from app import app
from app.forms import TagForm
import re
import sqlite3
from sqlite3 import Error
 

CREATE_TABLE_SQL = """CREATE TABLE IF NOT EXISTS 
	newsgroup_term(
		newsgroup TEXT, 
		term TEXT, 
		timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)"""

DB_NAME = 'app_db.sqlite3'

def save_results(res):
	try:
		con = sqlite3.connect(DB_NAME)
		cur = con.cursor()
		cur.execute(CREATE_TABLE_SQL)
		insert_sql = "insert into newsgroup_term(newsgroup, term) values (?,?)"
		termsA = re.split(', *', res[1])
		for tA in termsA:
			rec = (res[0], tA)
			cur.execute(insert_sql, rec)
		termsB = re.split(', *', res[3])
		for tB in termsB:
			rec = (res[2], tB)
			cur.execute(insert_sql, rec)
		con.commit()
		con.close()
	except Error as e:
		print(e)


def dump_results():
	q = "select newsgroup, term from newsgroup_term where term is not null and term is not '' order by newsgroup;"
	FIELD_SEP = ','
	rules = FIELD_SEP.join(['newsgroup','term']) + '\n'
	try:
		con = sqlite3.connect(DB_NAME)
		cur = con.cursor()
		cur.execute(q)
		for row in cur.fetchall():
			rules = rules + FIELD_SEP.join(row) + '\n'
		return rules
	except Error as e:
		print(e)
	return 'Sorry about that.'


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
	return [{'label':rpp[0][0], 'msg':rpp[0][1]}, {'label':rpp[1][0], 'msg':rpp[1][1]}]


@app.route('/rules')
def rules():
	rules_txt = dump_results()
	return Response(rules_txt, mimetype='text/plain')


@app.route('/')
@app.route('/index')
@app.route('/instructions')
def index():
	return render_template('index.html')


@app.route('/task', methods=['GET', 'POST'])
def task():
	# ngs = NewsgroupSampler.NewsgroupSampler() # ngs.
	rpp = get_random_pair_of_posts()
	tag_form = TagForm(newsgroupA=rpp[0]['label'], newsgroupB=rpp[1]['label'])
	if tag_form.validate_on_submit():
		tag_form_results = [tag_form.newsgroupA.data, tag_form.tagA.data, 
							tag_form.newsgroupB.data, tag_form.tagB.data]
		save_results(tag_form_results)
		flash("Thank you for entering these tags: '{}':'{}', '{}':'{}'".format(*tag_form_results))
		return redirect(url_for('task'))
	return render_template('task.html', rpp=rpp, form=tag_form)

