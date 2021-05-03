from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length, Regexp
from wtforms.fields import StringField
from wtforms.widgets import TextArea

# Set your classes here.

class RegisterForm(FlaskForm):
    name = TextField(
        'Username', validators=[DataRequired(), Regexp('/^[A-Za-z][A-Za-z0-9_-]*$/', message='Invalid characters present'), Length(min=6, max=25)]
    )
    password = PasswordField(
        'Password', validators=[DataRequired(), Length(min=6, max=40)]
    )

class LoginForm(FlaskForm):
    name = TextField('Username', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])

class JournalForm(FlaskForm):
    body = StringField(
        u'Text', widget=TextArea(), validators=[DataRequired(), Length(min=3)]
    )

class NetworkForm(FlaskForm):
    name = TextField('Username')