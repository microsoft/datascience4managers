from flask import render_template, flash, redirect, url_for, Response
from app import app
from app.forms import TagForm
import re
import psycopg2

from SECRETS import SECRETS

DB = psycopg2.connect(dbname=SECRETS['dbname'], user=SECRETS['user'], 
						host=SECRETS['host'], password=SECRETS['password'],
						port=SECRETS['port'])


def save_results(res, con):
	cur = con.cursor()
	insert_sql = "insert into newsgroup_term(newsgroup, term) values (%s,%s)"
	termsA = re.split(', *', res[1])
	for tA in termsA:
		rec = (res[0], tA)
		cur.execute(insert_sql, rec)
	termsB = re.split(', *', res[3])
	for tB in termsB:
		rec = (res[2], tB)
		cur.execute(insert_sql, rec)
	con.commit()
	cur.close()


def dump_results(con):
	q = """select newsgroup, term 
		from newsgroup_term 
		where term is not null and term != '' 
		order by newsgroup;""" #  and term != '' 
	FIELD_SEP = ','
	rules = FIELD_SEP.join(['newsgroup','term']) + '\n'
	cur = con.cursor()
	cur.execute(q)
	row = cur.fetchone()
	while row is not None:
		rules = rules + FIELD_SEP.join(row) + '\n'
		row = cur.fetchone()
	cur.close()
	return rules


def get_random_pair_of_posts(con):
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
	cur = con.cursor()
	cur.execute(rpp_query)
	rpp = []
	for row in cur.fetchall():
		rpp.append(row)
	return [{'label':rpp[0][0], 'msg':rpp[0][1]}, {'label':rpp[1][0], 'msg':rpp[1][1]}]


@app.route('/rules')
def rules():
	rules_txt = dump_results(DB)
	return Response(rules_txt, mimetype='text/plain')


@app.route('/')
@app.route('/index')
@app.route('/instructions')
def index():
	return render_template('index.html')


@app.route('/task', methods=['GET', 'POST'])
def task():
	rpp = get_random_pair_of_posts(DB)
	tag_form = TagForm(newsgroupA=rpp[0]['label'], newsgroupB=rpp[1]['label'])
	if tag_form.validate_on_submit():
		tag_form_results = [tag_form.newsgroupA.data, tag_form.tagA.data, 
							tag_form.newsgroupB.data, tag_form.tagB.data]
		save_results(tag_form_results, DB)
		flash("Thank you for entering these tags: {}:'{}', {}:'{}'".format(*tag_form_results))
		return redirect(url_for('task'))
	return render_template('task.html', rpp=rpp, form=tag_form)

