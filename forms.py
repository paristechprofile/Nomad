# import the tools and fields we need
from flask_wtf import FlaskForm as Form
from wtforms import TextField, TextAreaField, StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email, Length, EqualTo)
from models import User

def username_exists(form, field):
  if User.select().where(User.username == field.data).exists():
    raise ValidationError('User with that username already exists.')

def email_exists(form, field):
  if User.select().where(User.email == field.data).exists():
    raise ValidationError('User with that email already exists.')

class RegisterForm(Form):
  username = StringField(
    'Username',
    validators=[
      DataRequired(),
      Regexp(
        r'^[a-zA-Z0-9_]+$',
        message=("Username should be one word, letters, numbers, and underscores only.")
      ),
      username_exists
    ])
  email = StringField(
    'Email',
    validators=[
      DataRequired(),
      Email(),
      email_exists
    ])
  password = PasswordField(
    'Password',
    validators=[
      DataRequired(),
      Length(min=2),
      EqualTo('password2', message='Passwords must match')
    ])
  password2 = PasswordField(
    'Confirm Password',
    validators=[DataRequired()]
    )

class LoginForm(Form):
  email = StringField('Email', validators=[DataRequired(), Email()])
  password = PasswordField('Password', validators=[DataRequired()])

class New_Team_Form(Form):
  name = StringField('Name', validators=[DataRequired()])
  point_of_contact = StringField('Point of Contact')
  phone = StringField('Phone')
  email = StringField('Email', validators=[
    DataRequired(),
    Email(),
    email_exists
  ])

class Edit_Team_Form(Form):
  name = StringField('Name', validators=[DataRequired()])
  point_of_contact = StringField('Point of Contact')
  phone = StringField('Phone')
  email = StringField('Email')


class New_Parker_Form(Form):
  name = StringField('Name')
  email = StringField('Email')
  year = StringField('Year') 
  make = StringField('Make')
  model = StringField('Model')
  color = StringField('Color')
  license_plate = StringField('License Plate')
  license_state = StringField('License State')

class Edit_Parker_Form(Form):
  name = StringField('Name')
  email = StringField('Email')
  year = StringField('Year') 
  make = StringField('Make')
  model = StringField('Model')
  color = StringField('Color')
  license_plate = StringField('License Plate')
  license_state = StringField('License State')
  
class New_Vehicle_Form(Form):
  year = StringField('Year') 
  make = StringField('Make')
  model = StringField('Model')
  color = StringField('Color')
  license_plate = StringField('License Plate')
  license_state = StringField('License State')
  
class New_Facility_Form(Form):
  name = StringField('Name')
  email = StringField('Email') 
  address = StringField('Address')
  lat = StringField('Lat')
  long = StringField('Long')

class Admin_Edit_Facility_Form(Form):
  name = StringField('Name')
  email = StringField('Email') 
  address = StringField('Address')
  lat = StringField('Lat')
  long = StringField('Long')
  