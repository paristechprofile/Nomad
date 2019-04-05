from flask import Flask, g
from flask import render_template, flash, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_basicauth import BasicAuth
from flask_bcrypt import check_password_hash
import json
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
  g.db = models.DATABASE #peewee
  g.db.connect()
  g.user = current_user

@app.after_request
def after_request(res):
  """Close the database connection after each request."""
  g.db.close()
  return res

@app.route('/')
def index():
  # stream = models.Post.select().limit(100)
  return render_template('home.html')

@app.route('/admin')
@basic_auth.required
def secret_view():
  return render_template('home.html')

@app.route('/signup', methods=('GET', 'POST'))
def signup():
  form = forms.RegisterForm()
  if form.validate_on_submit():
    models.User.create_user(
      username=form.username.data,
      email=form.email.data,
      password=form.password.data
      )
    flash("You've been signed up, now just log-in", "success")
    return redirect(url_for('login'))
  return render_template('signup.html', form=form)

@app.route('/login', methods=('GET', 'POST'))
def login():
  form = forms.LoginForm()
  if form.validate_on_submit():
    try:
      user = models.User.get(models.User.email == form.email.data)
    except models.DoesNotExist:
      flash("your email or password doesn't match", "error")
    else:
      if check_password_hash(user.password, form.password.data):
        login_user(user)
        flash("You're in", 'success')
        return redirect(url_for('index'))
      else:
        flash("your email or password doesn't match", "error")
  return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
  logout_user()
  flash("You've been logged out", "success")
  return redirect(url_for('index'))

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
      flash('you saved the edited team')
      return redirect(url_for('teams'))
    else: 
      flash('Testing this team flash')
    return render_template("teams_edit.html", team=team,form=form)

@app.route('/teams/<id>/delete', methods=['GET', 'POST'])
@login_required
def delete_team(id):
  if current_user.is_admin: 
    team_param = int(id)
    team = models.Team.get_or_none(team_param)
    if str(team.id) == str(team_param):
      team.delete_instance()
      flash('you deleted the team')
      return redirect(url_for('teams'))
    else: 
      flash('We cannot delete the team flash')
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
      return redirect(url_for('teams'))
  return render_template('teams_new_team.html', form=form)
  
@app.route('/parkers')
@login_required
def parkers():
  if current_user.is_admin: 
    parkers = models.Parker.select().limit(100)
    return render_template('parkers_list.html', parkers=parkers)
  else: 
    parkers = models.Parker.select().limit(100)
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
        email=form.email.data.strip()
        )
      models.Vehicle.create(
        parker_id='99',
        make = form.make.data.strip(),
        year = form.year.data.strip(),
        model = form.model.data.strip(),
        color = form.color.data.strip(),
        license_plate=form.license_plate.data.strip(),
        license_state=form.license_state.data.strip()
      )
      breakpoint()
      return redirect(url_for('parkers'))
  else:
    if form.validate_on_submit():
      models.Parker.create(
        team_id=current_user.team_id,
        name=form.name.data.strip(), 
        email=form.email.data.strip(),
        )
      
      models.Vehicle.create(
        parker_id='99',
        make = form.make.data.strip(),
        year = form.year.data.strip(),
        model = form.model.data.strip(),
        color = form.color.data.strip(),
        license_plate=form.license_plate.data.strip(),
        license_state=form.license_state.data.strip()
      )
    return redirect(url_for('parkers'))
  return render_template('parkers_new_parker.html', form=form)

@app.route('/parkers/<id>/', methods=['GET', 'POST'])
@login_required
def edit_parkers(id):
  form = forms.Edit_Parker_Form()
  parker_param = int(id)
  parker = models.Parker.get(models.Parker.id == parker_param)
  if form.validate_on_submit():
    parker.name = form.name.data
    parker.email = form.email.data
    parker.save()
    flash('you saved the edited parker')
    return redirect(url_for('parkers'))
  else: 
    flash('Testing this parker flash')
    return render_template("parkers_edit.html", parker=parker,form=form)


@app.route('/vehicles')
@login_required
def vehicles(id=None):
  if id == None:
    vehicles = models.Vehicle.select().limit(100)
  return render_template('vehicles_list.html', vehicles=vehicles)

@app.route('/new_vehicle',methods=['GET', 'POST'])
@login_required
def new_vehicle():
  form = forms.New_Vehicle_Form()
  if form.validate_on_submit():
    models.Vehicle.create(
      # facility_id=
      # parker_id=
      make=form.make.data.strip(), 
      year=form.year.data.strip(),
      model=form.model.data.strip(),
      color=form.color.data.strip(),
      license_plate=form.license_plate.data.strip(),
      license_state=form.license_state.data.strip(),
      )
    return redirect(url_for('vehicles'))
  return render_template('vehicles_new_vehicle.html', form=form)

@app.route('/space')
@login_required
def facilities(id=None):
  if id == None:
    facilities = models.Facility.select().limit(100)
  return render_template('facilities_list.html', facilities=facilities)

@app.route('/space/<id>/', methods=['GET', 'POST'])
@login_required
def edit_facility(id):
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
    flash('you saved the edited facility')
    return redirect(url_for('facilities'))
  else: 
    flash('Testing this edit_facility flash')
    return render_template("facilities_edit.html", facility=facility,form=form)

@app.route('/space/<id>/delete', methods=['GET', 'POST'])
@login_required
def delete_facility(id):
  facility_param = int(id)
  facility = models.Facility.get_or_none(facility_param)
  if str(facility.id) == str(facility_param):
    facility.delete_instance()
    flash('you deleted the facility')
    return redirect(url_for('facilities'))
  else: 
    flash('We cannot delete the facility flash')
    return redirect(url_for('facilities'))

@app.route('/new_facility',methods=['GET', 'POST'])
@login_required
def new_facility():
  form = forms.New_Facility_Form()
  if form.validate_on_submit():
    models.Facility.create(
      name=form.name.data.strip(), 
      email=form.email.data.strip(),
      address=form.address.data.strip(),
      lat=form.lat.data.strip(),
      long=form.long.data.strip()
    )
    return redirect(url_for('facilities'))
  return render_template('facilities_new_facility.html', form=form)



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


# @app.route('/barbers')
# @app.route('/barbers/<id>/', methods=['GET', 'POST'])
# def barbers(id=None):
#   if request.args.get('neighborhood') == 'choose':
#     neighborhood_code = "ga"
#   else:
#     neighborhood_code = request.args.get('neighborhood')
#   neighborhood = neighborhoods_by_key.get(neighborhood_code)
#   form = forms.PostForm()
#   if id == None:
#     barbers = models.Barber.select().limit(100)
#     return render_template('barbers.html', barbers=barbers, form=form, neighborhood = neighborhood)
#   else:
#     barber_param = int(id)
#     barber = models.Barber.get(models.Barber.id == barber_param)
#     reviews = barber.reviews
#     form = ReviewForm()
#     if form.validate_on_submit():
#       models.Review.create(
#         barber=barber_param, 
#         user_id=g.user._get_current_object(),
#         text=form.text.data.strip(), 
#         rating=form.rating.data.strip()
#         )
#       flash("You created a review")
#     return render_template("barber.html", barber=barber, reviews=reviews,form=form, pub_key=pub_key)

# @app.route('/barbers/<barberid>/reviews/<id>/delete')
# def delete_review(barberid, id):
#   if request.args.get('neighborhood') == None:
#     neighborhood_code = "ga"
#   else:
#     neighborhood_code = request.args.get('neighborhood')
#   neighborhood = neighborhoods_by_key.get(neighborhood_code) # tab this over if necessary
#   review_param = int(id)
#   barber_param = int(barberid)
#   review = models.Review.get_or_none(review_param)
#   if str(review.user_id) == str(current_user.id):
#     review.delete_instance()
#     form = ReviewForm()
#     barber = models.Barber.get(models.Barber.id == barber_param)
#     reviews = barber.reviews
#     flash('you deleted your review')
#     return redirect(url_for('barbers', id=barber_param))
#   else:
#     flash('you cannot delete a review that is not yours')
#   return redirect(url_for('barbers', id=barber_param, neighborhood = neighborhood))

if 'ON_HEROKU' in os.environ:
  print('hitting ')
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
      email='fake@gmail.com',
      password='whynot',
      admin=True,
      team_id= 1
    )
    models.User.create_user(
      username='Amanda',
      email='amanda@preacher.com',
      password='pencil',
      admin=False,
      team_id= 2
    )
    models.User.create_user(
      username='John',
      email='john@preacher.com',
      password='pencil',
      admin=False,
      team_id= 2
    )
    models.Facility.create_facility(
      name="Littlefield",
      email="premier@gmail.com",
      address="800 Brazos",
      lat=37.7648532,
      long=-122.4222631
    )
    models.Facility.create_facility(
      name="Post Office",
      email="laz@gmail.com",
      address="400 congress",
      lat=37.7647382,
      long=-122.3883884
    )
    models.Vehicle.create_vehicle(
      year = "2009",
      make = "VW",
      model = "Jetta",
      color = "slate",
      license_plate = "3894hf",
      license_state = "TX",
      facility_id=1,
      parker_id=1
    )
    models.Vehicle.create_vehicle(
      year = "2009",
      make = "Ford",
      model = "Escort",
      color = "grey",
      license_plate = "2984hf",
      license_state = "CA",
      facility_id=2,
      parker_id=1
    )
    models.Vehicle.create_vehicle(
      year = "2014",
      make = "Mercedes",
      model = "AMG",
      color = "blue",
      license_plate = "0394fb",
      license_state = "TX",
      facility_id=3,
      parker_id=1
    )
    models.Vehicle.create_vehicle(
      year = "2019",
      make = "BWM",
      model = "335i",
      color = "silver",
      license_plate = "24on44",
      license_state = "TX",
      facility_id=4,
      parker_id=1
    )
    models.Parker.create_parker(
      team_id = 1,
      user_id =1,
      name = "Paris",
      email = "paris@gmail.com"
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

  except ValueError:
    pass
  app.run(debug=DEBUG, port=PORT)