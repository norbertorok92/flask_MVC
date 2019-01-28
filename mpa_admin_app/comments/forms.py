from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class CommentForm(FlaskForm):
  content = TextAreaField('Content', validators=[DataRequired()])
  submit = SubmitField('Post')
