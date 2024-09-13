from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class BookGenerationForm(FlaskForm):
    title = StringField('Book Title', validators=[DataRequired(), Length(max=100)])
    educational_objective = TextAreaField('Educational Objective', validators=[DataRequired()])
    age = IntegerField('Child\'s Age', validators=[DataRequired(), NumberRange(min=4, max=12)])
    characters = StringField('Characters', validators=[DataRequired()])
    setting = StringField('Setting', validators=[DataRequired()])
    book_length = SelectField('Book Length', choices=[
        ('short', 'Short (5-10 pages)'),
        ('medium', 'Medium (11-20 pages)'),
        ('long', 'Long (21-30 pages)')
    ], validators=[DataRequired()])
    submit = SubmitField('Generate Book')
