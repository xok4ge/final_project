from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField


class HokkyForm(FlaskForm):
    content = TextAreaField("Содержание")
    submit = SubmitField('Применить')