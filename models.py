import datetime
import os
from peewee import *
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash
# from playhouse.db_url import connect
from flask import g

DATABASE = connect(os.environ.get('DATABASE_URL'))
# DATABASE = PostgresqlDatabase('nomad') #local postgres backup
# DATABASE = SqliteDatabase('nomad.db') #local sqlitebackup if postgres is buggy

class Team(Model):
  name = CharField(unique=True)
  point_of_contact = CharField()
  phone = CharField()
  email = CharField(unique=True)
  
  class Meta:
    database = DATABASE
  
  @classmethod
  def create_team(cls, name, point_of_contact, phone, email):
    try:
      cls.create(
        name = name,
        point_of_contact = point_of_contact,
        phone = phone,
        email = email
      )
    except IntegrityError:
      raise ValueError("Team already exists")

class User(UserMixin, Model):
  username = CharField(unique=True)
  email = CharField(unique=True)
  password  = CharField(max_length=100)
  joined_at = DateTimeField(default=datetime.datetime.now)
  is_admin = BooleanField(default=False)
  team_id = ForeignKeyField(Team, backref='user')

  class Meta:
    database = DATABASE
  
  @classmethod
  def create_user(cls, team_id, username, email, password, admin=False):
    try:
      cls.create(
        username=username,
        email=email,
        password=generate_password_hash(password),
        is_admin=admin,
        team_id=team_id
      )
    except IntegrityError:
      raise ValueError("User already exists")

class Facility(Model):
  name = CharField()
  email = CharField()
  address = CharField()
  lat=CharField()
  long=CharField()
  
  class Meta:
    database = DATABASE
  
  @classmethod
  def create_facility(cls, name, email, address, lat, long):
    try:
      cls.create(
        name=name,
        email=email,
        address=address,
        lat=lat,
        long=long
      )
    except IntegrityError:
      raise ValueError("User already exists")

class Parker(Model):
  team_id = ForeignKeyField(Team, backref='parker', null=True)
  name = CharField()
  email = CharField()
  user_id = ForeignKeyField(User, backref='parker', null=True)
  
  class Meta:
    database = DATABASE

  @classmethod
  def create_parker(cls, team_id, user_id, name, email):
    try:
      cls.create(
        team_id = team_id,
        name = name,
        email = email,
        user_id =user_id
      )
    except IntegrityError:
      raise ValueError("Vehicle already exists")
      
class Vehicle(Model):
  year = CharField()
  make = CharField()
  model = CharField()
  color = CharField()
  license_plate = CharField(unique=True)
  license_state = CharField()
  facility_id = ForeignKeyField(Facility, backref='vehicle',null=True)
  parker_id = ForeignKeyField(Parker, backref='vehicle', null=True)

  
  class Meta:
    database = DATABASE
  
  @classmethod
  def create_vehicle(cls,facility_id, parker_id,year, make, model, color, license_plate, license_state):
    try:
      cls.create(
        year = year,
        make = make,
        model = model,
        color =color,
        license_plate =license_plate,
        license_state =license_state,
        facility_id=facility_id,
        parker_id=parker_id
      )
    except IntegrityError:
      raise ValueError("Vehicle already exists")


  
def initialize():
  DATABASE.connect()
  DATABASE.create_tables([Team, User, Vehicle, Parker, Facility], safe=True)
  DATABASE.close()