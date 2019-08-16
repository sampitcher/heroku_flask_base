from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Activity
import time
import json

from app.strava_api import get_activities as gatcs, get_activity_streams as gas, get_activity as gact, get_park_run_activities as gpra
from app import mappa_run

# def save_data(data_dict):
#     with open('data_file.json', 'w') as f:
#         f.write(json.dumps(data_dict))

# def load_data():
#     with open('data_file.json', 'r') as f:
#         data = json.loads(f.read())
#     return data

@app.route('/')

@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    # activities = [
    #     {'author': user, 'name': 'Test post #1'},
    #     {'author': user, 'name': 'Test post #2'}
    # ]
    # activities = current_user.activities.all()
    # activities = 'hello'

    activities = Activity.query.filter_by(author=current_user)
    return render_template('user.html', user=user, activities=activities)

@app.route('/mappa', methods=['GET', 'POST'])
def mappa():
    strava_code = current_user.strava_code
    return render_template("upload_connect_strava.html", strava_code=strava_code)

@app.route("/getstravacode", methods=["GET", "POST"])
def getstravacode():
    strava_code = request.args.get('code', '')
    username = current_user.username

    user = User.query.filter_by(username=username).first()
    user.strava_code = strava_code
    db.session.commit()

    strava_code = current_user.strava_code
    return render_template("upload_connect_strava.html", strava_code=strava_code)

@app.route('/sync', methods = ['GET', 'POST'])
@login_required
def sync():
	# delete activities first
    activities_delete = Activity.query.filter_by(author=current_user)
    for act in activities_delete:
        db.session.delete(act)
    db.session.commit()
    
    # reupload last 10 activities
    strava_code = current_user.strava_code
    timenow = current_user.timenow

    print(strava_code)
    activities = gatcs(1,strava_code)
    for i in range(len(activities)):
        activity_id = activities[i]['id']
        print(activity_id)
        name = activities[i]['name']
        print(name)
        name_id = '{}_{}_{}'.format(name,activity_id,timenow)

        try:
            elevation = activities[i]['elevation']
            print(elevation)
        except:
            elevation = '0'

        try:
            distance = activities[i]['distance']
            print(distance)
        except:
            distance = '0'

        try:
            duration = activities[i]['moving_time']
            print(duration)
        except:
            duration = '0'

        try:
            max_speed = activities[i]['max_speed']
            print(max_speed)
        except:
            max_speed = '0'

        try:
            avg_speed = activities[i]['average_speed']
            print(avg_speed)
        except:
            avg_speed = '0'

        try:
            max_power = activities[i]['max_power']
            print(max_power)
        except:
            max_power = '0'

        try:
            avg_power = activities[i]['avg_power']
            print(avg_power)
        except:
            avg_power = '0'

        try:
            max_heartrate = activities[i]['max_heartrate']
            print(max_heartrate)
        except:
            max_heartrate = '0'

        try:
            avg_heartrate = activities[i]['average_heartrate']
            print(avg_heartrate)
        except:
            avg_heartrate = '0'

        activity = Activity(name=name, activity_id=activity_id, elevation=elevation, distance=distance, duration=duration, max_speed=max_speed, avg_speed=avg_speed, max_power=max_power, avg_power=avg_power, max_heartrate=max_heartrate, avg_heartrate=avg_heartrate, name_id=name_id, author=current_user)
        db.session.add(activity)
        db.session.commit()

    return render_template("upload_connect_strava.html")

@app.route('/syncpr', methods = ['GET', 'POST'])
@login_required
def syncpr():
    # delete activities first
    activities_delete = Activity.query.filter_by(author=current_user)
    for act in activities_delete:
        db.session.delete(act)
    db.session.commit()
    
    # reupload last 10 activities
    strava_code = current_user.strava_code
    timenow = current_user.timenow

    print(strava_code)

    activities = gpra(strava_code)

    print(activities)

    for i in range(len(activities)):
        activity_id = activities[i]['act_id']
        print(activity_id)
        name = activities[i]['name']
        print(name)
        name_id = '{}_{}_{}'.format(name,activity_id,timenow)

        try:
            elevation = activities[i]['elevation']
            print(elevation)
        except:
            elevation = '0'

        try:
            distance = activities[i]['distance']
            print(distance)
        except:
            distance = '0'

        try:
            duration = activities[i]['moving_time']
            print(duration)
        except:
            duration = '0'

        try:
            max_speed = activities[i]['max_speed']
            print(max_speed)
        except:
            max_speed = '0'

        try:
            avg_speed = activities[i]['average_speed']
            print(avg_speed)
        except:
            avg_speed = '0'

        try:
            max_power = activities[i]['max_power']
            print(max_power)
        except:
            max_power = '0'

        try:
            avg_power = activities[i]['avg_power']
            print(avg_power)
        except:
            avg_power = '0'

        try:
            max_heartrate = activities[i]['max_heartrate']
            print(max_heartrate)
        except:
            max_heartrate = '0'

        try:
            avg_heartrate = activities[i]['average_heartrate']
            print(avg_heartrate)
        except:
            avg_heartrate = '0'

        activity = Activity(name=name, activity_id=activity_id, elevation=elevation, distance=distance, duration=duration, max_speed=max_speed, avg_speed=avg_speed, max_power=max_power, avg_power=avg_power, max_heartrate=max_heartrate, avg_heartrate=avg_heartrate, name_id=name_id, author=current_user)
        db.session.add(activity)
        db.session.commit()

    return render_template('index.html', user=user, activities=activities)

@app.route('/delete', methods = ['GET', 'POST'])
@login_required
def delete():
    activities_delete = Activity.query.filter_by(author=current_user)
    for act in activities_delete:
        db.session.delete(act)
    db.session.commit()

    return render_template("upload_connect_strava.html")

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      f.save(f.filename)
      # data_dict = {'filename': f.filename}

      timenow = int(time.time())
      # data_dict['timenow'] = timenow

      # save_data(data_dict)

      username = current_user.username

      user = User.query.filter_by(username=username).first()
      user.current_image = f.filename
      user.timenow = timenow
      db.session.commit()

      activity_names = []
      activity_ids = []
      blank_array = range(10)
      activities_select = Activity.query.filter_by(author=current_user)
      for act in activities_select:
        activity_names.append(act.name)
        activity_ids.append(act.activity_id)
      print(activity_names)
      return render_template("strava.html", filename=f.filename, activity_names=activity_names, activity_ids=activity_ids, blank_array=blank_array)

@app.route("/strava", methods=["GET", "POST"])
def strava():
    # data_dict = load_data()
    # base_image_location = data_dict['filename']
    # timenow = data_dict['timenow']

    timenow = current_user.timenow
    base_image_location = current_user.current_image

    if request.form:
        # username = current_user.username

        activity_id = request.form.get("activity_id")
        print(activity_id)

        # activity_id = strava_current_activities[activity_name]

        # activity_id = Activity.query.filter_by(author=current_user, name=activity_name).first_or_404()

        strava_code = current_user.strava_code
        image = mappa_run.create_image(activity_id, base_image_location, timenow, strava_code)
        # return render_template("final.html", activity_id = '', base_image = base_image_location)
        return render_template("final.html", activity_id = activity_id, base_image = base_image_location, timenow = timenow)

    else:
        return render_template("final.html", activity_id = '', base_image = base_image_location)

    #     if request.form:
    #     username = current_user.username
    #     strava_current_activities = current_user.strava_current_activities
    #     # data_dict = load_data()
    #     activity_id = request.form.get("activity_id")
    #     activity_name = request.form.get("activity_name")
    #     print(activity_name)

    #     activity_id = strava_current_activities[activity_name]
    #     # data_dict['activity_id'] = activity_id
    #     # save_data(data_dict)

    #     # load_data()

    #     # image = mappa_run.create_image(data_dict['activity_id'], base_image_location, timenow)
    #     strava_code = current_user.strava_code
    #     image = mappa_run.create_image(activity_id, base_image_location, timenow, strava_code)
    #     return render_template("final.html", activity_id = activity_id, base_image = base_image_location, timenow = timenow)

    # else:
    #     return render_template("final.html", activity_id = '', base_image = base_image_location)

