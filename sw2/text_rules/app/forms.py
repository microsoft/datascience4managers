from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField #, PasswordField, BooleanField
from wtforms.validators import DataRequired

class TagForm(FlaskForm):
	newsgroupA = HiddenField('newsgroupA')
	tagA = StringField('tag') # , validators=[DataRequired()]
	newsgroupB = HiddenField('newsgroupB')
	tagB = StringField('tag')
	submit = SubmitField('Submit')