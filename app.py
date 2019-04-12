from flask import Flask, g
from flask import render_template, flash, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_basicauth import BasicAuth
from flask_bcrypt import check_password_hash
import json
import requests
import models
import forms
from flask_bootstrap import Bootstrap
import os
import stripe

pub_key = "pk_test_Gw8IVbbM8DOAEaBbLL0kTgyb00Y5uaJJYF"
secret_key = "sk_test_CseTb8EzJjxwSu0xORFMR2wB00LUU3wFPU"
stripe.api_key = secret_key 

DEBUG = True
PORT = 8000

app = Flask(__name__, static_url_path='/static')
basic_auth = BasicAuth(app)
app.secret_key = '!ohy.ouf.ancyh.uh?'
app.config['FLASK_ADMIN_SWATCH'] = 'darkly'
app.config['BASIC_AUTH_USERNAME'] = 'abc'
app.config['BASIC_AUTH_PASSWORD'] = '123'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(userid):
  try:
    return models.User.get(models.User.id == userid)
  except models.DoesNotExist:
    return None

@app.before_request
def before_request():
  """Connect to the database before each request."""
  g.db = models.DATABASE 
  g.db.connect()
  g.user = current_user

@app.after_request
def after_request(res):
  """Close the database connection after each request."""
  g.db.close()
  return res

@app.route('/')
def index():
  return render_template('home.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Authentication
@app.route('/admin')
@basic_auth.required
def secret_view():
  return render_template('home.html')

@app.route('/signup', methods=('GET', 'POST'))
def signup():
  form = forms.RegisterForm()
  if form.validate_on_submit():
    try:
      stripe_id = stripe.Customer.create(
        email=form.email.data
      ).id
      pass
    except stripe.error.CardError as e:
      # Since it's a decline, stripe.error.CardError will be caught
      body = e.json_body
      err  = body.get('error', {})
      print ("Status is: %s" % e.http_status)
      print ("Type is: %s" % err.get('type'))
      print ("Code is: %s" % err.get('code'))
      # param is '' in this case
      print ("Param is: %s" % err.get('param'))
      print ("Message is: %s" % err.get('message'))
    except stripe.error.RateLimitError as e:
      # Too many requests made to the API too quickly
      pass
    except stripe.error.InvalidRequestError as e:
      # Invalid parameters were supplied to Stripe's API
      pass
    except stripe.error.AuthenticationError as e:
      # Authentication with Stripe's API failed
      # (maybe you changed API keys recently)
      pass
    except stripe.error.APIConnectionError as e:
      # Network communication with Stripe failed
      pass
    except stripe.error.StripeError as e:
      # Display a very generic error to the user, and maybe send
      # yourself an email
      pass
    except Exception as e:
      # Something else happened, completely unrelated to Stripe
      pass
    models.User.create_user(
      team_id=1,
      username=form.username.data,
      password=form.password.data,
      email=form.email.data,
      stripe_id=stripe_id
    )
    flash("You're signed up, now just log-in", "success")
    return redirect(url_for('login'))
  else:
    flash("ERROR", "error")
  return render_template('signup.html', form=form)

@app.route('/login', methods=('GET', 'POST'))
def login():
  form = forms.LoginForm()
  if form.validate_on_submit():
    try:
      user = models.User.get(models.User.email == form.email.data)
    except models.DoesNotExist:
      flash("Your email or password doesn't match", "error")
    else:
      if check_password_hash(user.password, form.password.data):
        login_user(user)
        flash("Welcome back!", 'success')
        return redirect(url_for('index'))
      else:
        flash("Your email or password doesn't match", "error")
  return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
  logout_user()
  flash("You've been logged out", "success")
  return redirect(url_for('index'))

# Team views
@app.route('/teams')
@login_required
def teams(id=None):
  if current_user.is_admin: 
    teams = models.Team.select().limit(100)
  return render_template('teams_list.html', teams=teams)

@app.route('/teams/<id>/', methods=['GET', 'POST'])
@login_required
def edit_teams(id):
  form = forms.Edit_Team_Form()
  team_param = int(id)
  team = models.Team.get(models.Team.id == team_param)
  if current_user.is_admin: 
    if form.validate_on_submit():
      team.name = form.name.data
      team.point_of_contact = form.point_of_contact.data
      team.phone = form.phone.data
      team.email = form.email.data
      team.save()
      flash('You successfully saved the edited team')
      return redirect(url_for('teams'))
    else: 
      flash('Error saving team to database')
    return render_template("teams_edit.html", team=team,form=form)

@app.route('/teams/<id>/delete', methods=['GET', 'POST'])
@login_required
def delete_team(id):
  if current_user.is_admin: 
    team_param = int(id)
    team = models.Team.get_or_none(team_param)
    if str(team.id) == str(team_param):
      team.delete_instance()
      flash('You deleted the team')
      return redirect(url_for('teams'))
    else: 
      flash('Error deleting the team')
  return redirect(url_for('teams'))

@app.route('/new_team', methods=['GET', 'POST'])
@login_required
def new_team():
  form = forms.New_Team_Form()
  if current_user.is_admin: 
    if form.validate_on_submit():
      models.Team.create(
        name=form.name.data.strip(),
        point_of_contact=form.point_of_contact.data.strip(), 
        phone=form.phone.data.strip(), 
        email=form.email.data.strip()
      )
      flash('You created a new team')
      return redirect(url_for('teams'))
    else:
      flash('Error creating a new team')
  return render_template('teams_new_team.html', form=form)

# Parker views
@app.route('/parkers')
@login_required
def parkers():
  if current_user.is_admin: 
    parkers = models.Parker.select().limit(100)
    return render_template('parkers_list.html', parkers=parkers)
  else: 
    parkers = models.Parker.select().where(current_user.team_id.id == models.Parker.team_id)
    return render_template('parkers_list.html', parkers=parkers)

@app.route('/new_parker', methods=['GET', 'POST'])
@login_required
def new_parker():
  form = forms.New_Parker_Form()
  team = current_user.team_id
  if current_user.is_admin: 
    if form.validate_on_submit():
      models.Parker.create(
        team_id=current_user.team_id,
        name=form.name.data.strip(), 
        email=form.email.data.strip(),
        user_id=current_user.id,
        )
      parker_id = models.Parker.select().order_by(models.Parker.id.desc()).get()
      models.Vehicle.create(
        parker_id=parker_id.id,
        make = form.make.data.strip(),
        year = form.year.data.strip(),
        model = form.model.data.strip(),
        color = form.color.data.strip(),
        license_plate=form.license_plate.data.strip(),
        license_state=form.license_state.data.strip()
      )
      flash('You added a new parker')
      return redirect(url_for('parkers'))
    else:
      return render_template('parkers_new_parker.html', form=form)
  else:
    if form.validate_on_submit():
      models.Parker.create(
        team_id=current_user.team_id,
        user_id=current_user.id,
        name=form.name.data.strip(), 
        email=form.email.data.strip()
      )
      parker_id = models.Parker.select().order_by(models.Parker.id.desc()).get()
      models.Vehicle.create(
        parker_id=parker_id.id,
        make = form.make.data.strip(),
        year = form.year.data.strip(),
        model = form.model.data.strip(),
        color = form.color.data.strip(),
        license_plate=form.license_plate.data.strip(),
        license_state=form.license_state.data.strip()
      )
      flash('You added a new parker')
      return redirect(url_for('parkers'))
    else:
      return render_template('parkers_new_parker.html', form=form)

@app.route('/parkers/<id>/', methods=['GET', 'POST'])
@login_required
def edit_parkers(id):
  form = forms.Edit_Parker_Form()
  parker_param = int(id)
  parker = models.Parker.get(models.Parker.id == parker_param)
  vehicle = models.Vehicle.get(models.Vehicle.parker_id == parker_param)
  if form.validate_on_submit():
    parker.name = form.name.data
    parker.email = form.email.data
    vehicle.make = form.make.data
    vehicle.year = form.year.data
    vehicle.model = form.model.data
    vehicle.color = form.color.data
    vehicle.license_plate = form.license_plate.data
    vehicle.license_state = form.license_state.data
    vehicle.save()
    parker.save()
    flash('You saved the edited parker')
    return redirect(url_for('parkers'))
  else: 
    flash('Error editing the parker')
    return render_template("parkers_edit.html", parker=parker, vehicle=vehicle, form=form)

@app.route('/parkers/<id>/delete', methods=['GET', 'POST'])
@login_required
def delete_parker(id):
  if current_user.is_admin: 
    parker_param = int(id)
    parker = models.Parker.get(models.Parker.id == parker_param)
    vehicle = models.Vehicle.get(models.Vehicle.parker_id == parker_param)
    if str(parker.id) == str(parker_param):
      vehicle.delete_instance()
      parker.delete_instance()
      flash('You deleted the parker')
      return redirect(url_for('parkers'))
    else: 
      flash('Error deleting the parker')
  else:
    parker_param = int(id)
    parker = models.Parker.get(models.Parker.id == parker_param)
    vehicle = models.Vehicle.get_or_none(models.Vehicle.parker_id == parker_param)
    if vehicle:
      if str(parker.id) == str(parker_param):
        vehicle.delete_instance()
        parker.delete_instance()
        flash('You deleted the parker')
        return redirect(url_for('parkers'))
    else: 
      parker.delete_instance()
  return redirect(url_for('parkers'))

# Vehicle views
@app.route('/vehicles')
@login_required
def vehicles(id=None):
  if id == None:
    vehicles = models.Vehicle.select().limit(100)
  return render_template('vehicles_list.html', vehicles=vehicles)

@app.route('/parkers/<id>/add_vehicle',methods=['GET', 'POST'])
@login_required
def add_vehicle(id):
  form = forms.New_Vehicle_Form()
  team = current_user.team_id
  parker_param = int(id)
  parker = models.Parker.get_or_none(parker_param)
  vehicle = models.Vehicle.get_or_none(parker_param)
  if form.validate_on_submit():
    models.Vehicle.create(
      parker_id=id,
      make=form.make.data.strip(), 
      year=form.year.data.strip(),
      model=form.model.data.strip(),
      color=form.color.data.strip(),
      license_plate=form.license_plate.data.strip(),
      license_state=form.license_state.data.strip(),
      )
    flash('You added a vehicle')
    return redirect(url_for('parkers'))
  return render_template('vehicles_new_vehicle.html', vehicle=vehicle, parker=parker, form=form)

@app.route('/vehicles/<id>/', methods=['GET', 'POST'])
@login_required
def edit_vehicles(id):
  form = forms.New_Vehicle_Form()
  vehicle_param = int(id)
  vehicle = models.Vehicle.get(models.Vehicle.id == vehicle_param)
  if form.validate_on_submit():
    vehicle.make = form.make.data
    vehicle.year = form.year.data
    vehicle.model = form.model.data
    vehicle.color = form.color.data
    vehicle.license_plate = form.license_plate.data
    vehicle.license_state = form.license_state.data
    vehicle.save()
    flash('You saved the edited vehicle')
    return redirect(url_for('vehicles'))
  else: 
    flash('Error editing the vehicle')
    return render_template("vehicles_edit.html", vehicle=vehicle, form=form)

@app.route('/vehicles/<id>/delete', methods=['GET', 'POST'])
@login_required
def delete_vehicle(id):
  if current_user.is_admin: 
    vehicle_param = int(id)
    vehicle = models.Vehicle.get_or_none(vehicle_param)
    if str(vehicle.id) == str(vehicle_param):
      vehicle.delete_instance()
      flash('You deleted the vehicle')
      return redirect(url_for('vehicles'))
    else: 
      flash('Error deleting the vehicle')
  else:
    vehicle_param = int(id)
    vehicle = models.Vehicle.get_or_none(vehicle_param)
    if str(vehicle.id) == str(vehicle_param):
      vehicle.delete_instance()
      flash('You deleted the vehicle')
      return redirect(url_for('vehicles'))
    else: 
      flash('Error deleting the vehicle')
  return redirect(url_for('vehicles'))

# Facility views  
@app.route('/space')
@login_required
def facilities(id=None):
  if id == None:
    facilities = models.Facility.select().limit(100)
  return render_template('facilities_list.html', facilities=facilities)

@app.route('/space/map')
@login_required
def map_view():
  return render_template('facilities_map.html')

@app.route('/space/<id>/', methods=['GET', 'POST'])
@login_required
def edit_facility(id):
  if current_user.is_admin: 
    form = forms.Admin_Edit_Facility_Form()
    facility_param = int(id)
    facility = models.Facility.get(models.Facility.id == facility_param)
    if form.validate_on_submit():
      facility.name = form.name.data
      facility.email = form.email.data
      facility.address = form.address.data
      facility.lat = form.lat.data
      facility.long = form.name.data
      facility.save()
      flash('You saved the edited facility')
      return redirect(url_for('facilities'))
    else: 
      flash('Error editing the facility')
      return render_template("facilities_edit.html", facility=facility,form=form)

@app.route('/space/<id>/delete', methods=['GET', 'POST'])
@login_required
def delete_facility(id):
  if current_user.is_admin: 
    facility_param = int(id)
    facility = models.Facility.get_or_none(facility_param)
    if str(facility.id) == str(facility_param):
      facility.delete_instance()
      flash('You deleted the facility')
      return redirect(url_for('facilities'))
    else: 
      flash('Error deleting the facility')
      return redirect(url_for('facilities'))

@app.route('/new_facility',methods=['GET', 'POST'])
@login_required
def new_facility():
  if current_user.is_admin: 
    form = forms.New_Facility_Form()
    if form.validate_on_submit():
      models.Facility.create(
        name=form.name.data.strip(), 
        email=form.email.data.strip(),
        address=form.address.data.strip(),
        lat=form.lat.data.strip(),
        long=form.long.data.strip()
      )
      flash('You created a new facility')
      return redirect(url_for('facilities'))
    else: 
      flash('Error creating a new facility')
      return render_template('facilities_new_facility.html', form=form)

# Stripe integration
@app.route('/pay', methods = ['POST'])
def pay():
  print(request.form)
  customer = stripe.Customer.create(
    email = request.form['stripeEmail'], 
    source = request.form['stripeToken']
  )
  charge = stripe.Charge.create(
    customer = customer.id,
    amount = 999,
    currency = 'usd',
    description = 'Parking'
  )
  return '{} paid 9.99. Thanks!'.format(charge.customer)

@app.route('/invoices', methods=['GET'])
@login_required
def get_invoices():
  invoices = stripe.Invoice.list(limit=12)
  try:
    # Use Stripe's library to make requests...
    pass
  except stripe.error.CardError as e:
    # Since it's a decline, stripe.error.CardError will be caught
    body = e.json_body
    err  = body.get('error', {})

    print ("Status is: %s" % e.http_status)
    print ("Type is: %s" % err.get('type'))
    print ("Code is: %s" % err.get('code'))
    # param is '' in this case
    print ("Param is: %s" % err.get('param'))
    print ("Message is: %s" % err.get('message'))
  except stripe.error.RateLimitError as e:
    # Too many requests made to the API too quickly
    pass
  except stripe.error.InvalidRequestError as e:
    # Invalid parameters were supplied to Stripe's API
    pass
  except stripe.error.AuthenticationError as e:
    # Authentication with Stripe's API failed
    # (maybe you changed API keys recently)
    pass
  except stripe.error.APIConnectionError as e:
    # Network communication with Stripe failed
    pass
  except stripe.error.StripeError as e:
    # Display a very generic error to the user, and maybe send
    # yourself an email
    pass
  except Exception as e:
    # Something else happened, completely unrelated to Stripe
    pass
  return render_template('invoices.html', invoices=invoices)


if 'ON_HEROKU' in os.environ:
  print('hitting')
  models.initialize()

if __name__ == '__main__':
  models.initialize()
  try:
    models.Team.create_team(
      name = 'Nomad',
      point_of_contact = 'Paris Taylor',
      phone = '512.987.7556',
      email = 'paris@nomadparking.space'
    )
    models.Team.create_team(
      name = 'Preacher',
      point_of_contact = 'John',
      phone = '512.999.9999',
      email = 'john@preacher.com'
    )
    models.User.create_user(
      username='paris',
      email='paris@nomadparking.space',
      password='whynot',
      admin=True,
      team_id= 1,
      stripe_id='1'
    )
    models.User.create_user(
      username='Amanda',
      email='amanda@preacher.com',
      password='pencil',
      admin=False,
      team_id= 2,
      stripe_id='2'
    )
    models.User.create_user(
      username='John',
      email='john@preacher.com',
      password='pencil',
      admin=False,
      team_id= 2,
      stripe_id='3'
    )
    models.Facility.create_facility(
      name="Post Office",
      email="laz@gmail.com",
      address="400 congress",
      lat=37.7647382,
      long=-122.3883884
    )
    models.Facility.create_facility(
      name="Littlefield",
      email="premier@gmail.com",
      address="800 Brazos",
      lat=37.7648532,
      long=-122.4222631
    )
    models.Parker.create_parker(
      team_id = 1,
      user_id =1,
      name = "Paris",
      email = "paris@nomadparking.com"
    )
    models.Parker.create_parker(
      team_id = 2,
      user_id =2,
      name = "Amanda",
      email = "amanda@preacher.com"
    )
    models.Parker.create_parker(
      team_id = 2,
      user_id =3,
      name = "John",
      email = "john@preacher.com"
    )
    models.Parker.create_parker(
      team_id = 2,
      user_id =4,
      name = "Krystle",
      email = "Krystle@preacher.com"
    )
    models.Vehicle.create_vehicle(
      year = "2009",
      make = "VW",
      model = "Jetta",
      color = "slate",
      license_plate = "3894hf",
      license_state = "TX",
      facility_id=1,
      parker_id=2
    )
    models.Vehicle.create_vehicle(
      year = "2009",
      make = "Ford",
      model = "Escort",
      color = "grey",
      license_plate = "2984hf",
      license_state = "CA",
      facility_id=2,
      parker_id=3
    )
    models.Vehicle.create_vehicle(
      year = "2014",
      make = "Mercedes",
      model = "AMG",
      color = "blue",
      license_plate = "0394fb",
      license_state = "TX",
      facility_id=2,
      parker_id=2
    )
    models.Vehicle.create_vehicle(
      year = "2019",
      make = "BWM",
      model = "335i",
      color = "silver",
      license_plate = "24on44",
      license_state = "TX",
      facility_id=2,
      parker_id=1
    )

  except ValueError:
    pass
  app.run(debug=DEBUG, port=PORT)