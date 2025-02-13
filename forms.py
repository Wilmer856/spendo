from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, FloatField, SelectField, DateField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Lasst Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',  validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

class UpdateUserForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',  validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')])

class AddTransactionForm(FlaskForm):
    category = SelectField("Category", choices=["Food & Dining", "Rent & Utilities", "Shopping", "Entertainment"], validators=[DataRequired()])
    amount = FloatField("Amount", validators=[DataRequired()])
    description = StringField("Description", validators=[Length(max=100)])

class ApplyFilterForm(FlaskForm):
    category = SelectField("Category", choices=["All", "Food & Dining", "Rent & Utilities", "Shopping", "Entertainment"])
    date = DateField("Date", format="%m-%d-%Y")
    min_amount = IntegerField("Min Amount")
    max_amount = IntegerField("Max Amount")
    submit = SubmitField("Apply Filters")