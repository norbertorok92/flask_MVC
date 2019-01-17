from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateField
from wtforms.validators import DataRequired

class EventForm(FlaskForm):
  title = StringField('Title', validators=[DataRequired()])
  content = TextAreaField('Content', validators=[DataRequired()])
  event_date = DateField('Event Date', validators=[DataRequired()])
  submit = SubmitField('Post Event')