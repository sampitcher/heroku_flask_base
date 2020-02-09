from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Activity
import time
import json

from app.strava_sdk import get_tokens_with_code as get_tokens_w_c, get_tokens_with_refresh_token as get_tokens_w_rt, get_activities as get_acts, get_athlete_id as get_ath_id, get_num_of_activities as get_num_acts
from app.pbl import get_embed_user as pbl_get_user, generate as pbl_generate

def get_access_token():
    username = current_user.username
    user = User.query.filter_by(username=username).first()
    expires_at = int(user.expires_at)
    refresh_token = user.refresh_token
    time_now = time.time()

    if(expires_at<time_now):
        print('Access Token is not valid, need to refresh token...')
        access_token, refresh_token, expires_at = get_tokens_w_rt(refresh_token)
        user.access_token = access_token
        user.refresh_token = refresh_token
        user.expires_at = expires_at
        db.session.commit()

    access_token = user.access_token
    refresh_token = user.refresh_token
    expires_at = user.expires_at

    return(access_token)

def generate_embed_url(username, location):
    user = pbl_get_user(username)
    embed_url = pbl_generate(user, location)
    return(embed_url)

@app.route('/')

@app.route('/index')
@login_required
def index():
    username = current_user.username
    location = "dashboards/7"
    embed_url = generate_embed_url(username, location)
    return render_template('index.html', title='Home', embed_url=embed_url)

@app.route('/running')
@login_required
def running():
    username = current_user.username
    location = "looks/6"
    embed_url = generate_embed_url(username, location)
    return render_template('running.html', title='Running', embed_url=embed_url)

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data).first()
#         if user is None or not user.check_password(form.password.data):
#             flash('Invalid username or password')
#             return redirect(url_for('login'))
#         login_user(user, remember=form.remember_me.data)
#         next_page = request.args.get('next')
#         if not next_page or url_parse(next_page).netloc != '':
#             next_page = url_for('index')
#         return redirect(next_page)
#     return render_template('login.html', title='Sign In', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            message = 'Invalid username or password!'
            return render_template('login.html', title='Register', message=message)
            return redirect(url_for('login'))
        # login_user(user, remember=form.remember_me.data)
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', message=message)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(username=form.username.data, email=form.email.data)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         flash('Congratulations, you are now a registered user!')
#         return redirect(url_for('login'))
#     return render_template('register.html', title='Register', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ""

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.form:
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        repeat_password = request.form.get('repeat_password')

        if len(username) < 3:
            message = 'You must enter a username!'
            return render_template('register.html', title='Register', message=message)
        if len(email) < 3:
            message = 'You must enter a email!'
            return render_template('register.html', title='Register', message=message)
        if len(password) < 3:
            message = 'You must enter a password!'
            return render_template('register.html', title='Register', message=message)
        if not password == repeat_password:
            message = "You're passwords must match!"
            return render_template('register.html', title='Register', message=message)
        user = User.query.filter_by(username=username).first()
        if user is None:
            print("success")
        else:
            print("exists")
            message = "This username already exists!"
            return render_template('register.html', title='Register', message=message)
            return redirect(url_for('register'))
        # user = User(username=username, email=email)
        # user.set_password(form.password.data)
        # db.session.add(user)
        # db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', message=message)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()

    activities = Activity.query.filter_by(author=current_user)

    # username = current_user.username
    location = "looks/5"
    embed_url = generate_embed_url(username, location)

    return render_template('user.html', user=user, activities=activities, embed_url=embed_url)

@app.route("/getstravacode", methods=["GET", "POST"])
@login_required
def getstravacode():
    strava_code = request.args.get('code', '')
    username = current_user.username

    access_token, refresh_token, expires_at = get_tokens_w_c(strava_code)

    user = User.query.filter_by(username=username).first()
    user.strava_code = strava_code
    user.access_token = access_token
    user.refresh_token = refresh_token
    user.expires_at = expires_at
    db.session.commit()

    athlete_id = get_ath_id(access_token)

    embed_url = generate_embed_url()

    return render_template("index.html", user=user, embed_url=embed_url)


@app.route('/sync', methods = ['GET', 'POST'])
@login_required
def sync():
    access_token = get_access_token()

    max_epoch = db.session.query(db.func.max(Activity.epoch)).scalar()
    print(max_epoch)

    activities = get_acts(access_token, max_epoch)

    for activity in activities:
        activity = Activity(
            activity_id=activity['activity_id'],
            name=activity['name'],
            activity_type=activity['activity_type'],
            epoch=activity['epoch'],
            # timenow=activity['timenow'],
            timestamp=activity['timestamp'],
            user_id=activity['user_id'],
            elevation=activity['elevation'],
            distance=activity['distance'],
            duration=activity['duration'],
            max_speed=activity['max_speed'],
            avg_speed=activity['avg_speed'],
            max_power=activity['max_power'],
            avg_power=activity['avg_power'],
            max_heartrate=activity['max_heartrate'],
            avg_heartrate=activity['avg_heartrate'],
            name_id=activity['name']+'_'+str(activity['activity_id']),
            author=current_user)
        db.session.add(activity)
        db.session.commit()

    print(activities)

    # username = current_user.username
    # user = User.query.filter_by(username=username).first()
    # athlete_id = user.athlete_id

    # get_num_acts(access_token, athlete_id)

    embed_url = generate_embed_url()

    return render_template("index.html", user=user, embed_url=embed_url)


@app.route('/delete', methods = ['GET', 'POST'])
@login_required
def delete():
    activities_delete = Activity.query.filter_by(author=current_user)
    for act in activities_delete:
        db.session.delete(act)
    db.session.commit()

    embed_url = generate_embed_url()

    return render_template("index.html", embed_url=embed_url)

@app.route("/update_athlete_id", methods=["GET", "POST"])
@login_required
def update_athlete_id():

    access_token = get_access_token()
    athlete_id = get_ath_id(access_token)

    username = current_user.username
    user = User.query.filter_by(username=username).first()
    user.athlete_id = athlete_id
    db.session.commit()

    embed_url = generate_embed_url()

    return render_template("index.html", user=user, embed_url=embed_url)

@app.route('/test', methods = ['GET', 'POST'])
def test():
    if request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        print(username)
        print(password)
    return render_template("test.html", filename='main.css')
