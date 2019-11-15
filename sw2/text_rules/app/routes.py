from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import TagForm
from NewsgroupSampler import NewsgroupSampler

@app.route('/')
@app.route('/index')
@app.route('/instructions')
def index():
	return render_template('index.html')

@app.route('/task', methods=['GET', 'POST'])
def task():
	ngs = NewsgroupSampler.NewsgroupSampler()
	rpp = ngs.get_random_pair_of_posts()
	tag_form = TagForm(newsgroupA=rpp[0]['label'], newsgroupB=rpp[1]['label'])
	if tag_form.validate_on_submit():
		tag_form_results = [tag_form.newsgroupA.data, tag_form.tagA.data, 
							tag_form.newsgroupB.data, tag_form.tagB.data]
		flash("Thank you for entering these tags: '{}':'{}', '{}':'{}'".format(*tag_form_results))
		return redirect(url_for('task'))
	return render_template('task.html', rpp=rpp, form=tag_form)

