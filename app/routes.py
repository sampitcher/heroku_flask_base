from flask import render_template, flash, redirect, url_for, request, make_response, Response
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Activity
import pandas as pd
import numpy as np
import time
import json

from app.strava_sdk import get_tokens_with_code as get_tokens_w_c, get_tokens_with_refresh_token as get_tokens_w_rt, get_activities as get_acts, get_athlete_id as get_ath_id, get_num_of_activities as get_num_acts, get_activity as get_act, get_activity_streams as get_act_streams, get_activity_laps as get_act_laps
from app.pbl import get_embed_user as pbl_get_user, generate as pbl_generate
from app.imager import normalise_data as norm_data, draw_route as drw_route, post_image_str as post_img

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
    resp = make_response(render_template('index.html', title='Home', embed_url=embed_url))
    resp.headers.add('Access-Control-Allow-Origin', 'http://pitcherpakeman001.lookersandbox.com')
    resp.headers.add('Access-Control-Allow-Credentials', 'true')
    resp.set_cookie('strava-pitcherpakeman-test', value='this is a test', domain=".lookersandbox.com", samesite=None)
    print(resp)
    return resp

@app.route('/activity_stats', methods=['GET', 'POST'])
@login_required
def activity_stats():
    act_streams = ''
    my_image_url = ''
    username = current_user.username
    if request.form:
        activity_id = request.form.get('activity_id')
        print(activity_id)
        access_token = get_access_token()
        act_streams = get_act_streams(access_token, activity_id)
        # print(act_streams['latlng'])

        lat_lng_data = act_streams['latlng']
        normalised_route = norm_data(lat_lng_data)
        my_image_string = drw_route(normalised_route)
        api_key = 'a2bfa0b4f13fb01cec47fd7fa307ff8f'
        my_image_url = post_img(api_key, my_image_string)


    response = make_response(render_template('activity_stats.html', title='Activity Stats', act_streams=act_streams, my_image_url=my_image_url))
    return response

@app.route('/running')
@login_required
def running():
    username = current_user.username
    location = "looks/6"
    embed_url = generate_embed_url(username, location)
    response = make_response(render_template('running.html', title='Running', embed_url=embed_url))
    response.set_cookie('same-site-cookie', 'https://lookersandbox.com', samesite=None);
    response.set_cookie('cross-site-cookie', 'https://lookersandbox.com', samesite=None, secure=True)
    return response

@app.route('/parkrun')
@login_required
def parkrun():
    username = current_user.username
    location = "dashboards/8"
    embed_url = generate_embed_url(username, location)
    response = make_response(render_template('parkrun.html', title='Parkrun', embed_url=embed_url))

    response.set_cookie('same-site-cookie', 'lookersandbox.com', samesite='Lax');
    response.set_cookie('cross-site-cookie', 'lookersandbox.com', samesite='Lax', secure=True)
    return response

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
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', message=message)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()

    activities = Activity.query.filter_by(author=current_user)

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

    username = current_user.username
    location = "dashboards/7"
    embed_url = generate_embed_url(username, location)

    return render_template("index.html", user=user, embed_url=embed_url)


@app.route('/sync', methods = ['GET', 'POST'])
@login_required
def sync():
    username = current_user.username
    user = User.query.filter_by(username=username).first()
    user_id = user.id
    access_token = get_access_token()
    print(f'user id: {user_id}')

    max_epoch = db.session.query(db.func.max(Activity.epoch)).filter(Activity.user_id == user_id).scalar()
    # max_epoch = db.session.query(db.func.max(Activity.epoch)).scalar()

    print(max_epoch)

    activities = get_acts(access_token, max_epoch)

    for activity in activities:
        ####################
        # ACTIVITY STREAMS #
        ####################

        # Run the act_streams function in strava_sdk to get the streams data
        act_streams = get_act_streams(access_token, activity['activity_id'])
        # Add a new dictionary which has the same time keys as the act_streams for a join on time to fill the time gaps
        act_streams_times = {'time_key' :range(max(act_streams['time_key'])+1), 'time_new' :range(max(act_streams['time_key'])+1)}

        # Turn them both into dataframes
        df = pd.DataFrame(act_streams)
        df_times = pd.DataFrame(act_streams_times)

        # Join them and fill in the gaps
        df_final = df_times.set_index('time_key').join(df.set_index('time_key')).interpolate()
        # Turn the NaN's to nulls for postgres
        df_final.replace({np.nan:None})
        # Turn the dataframe to a list
        act_streams_interpolated = df_final.replace({np.nan:None}).to_dict(orient='list')

        ####################
        # ROLLING AVERAGES #
        ####################

        # List of the rolling averages for hr, power and speed
        rollings = [1,5,10,20,30,45,60,120,300,600,1200]
        rolling_dict = {}
        for i in rollings:
            rolling_avg = df_final.replace({np.nan:None}).rolling(i, win_type='triang').mean()
            maxs = rolling_avg.max()
            try:
                max_hr = maxs.heartrate
            except:
                max_hr = None
            try:
                max_power = maxs.watts
            except:
                max_power = None
            try:
                max_speed = maxs.velocity_smooth
            except:
                max_speed = None

            rolling_dict[f'max_hr_{i}'] = max_hr
            rolling_dict[f'max_power_{i}'] = max_power
            rolling_dict[f'max_speed_{i}'] = max_speed
        
        # print(rolling_dict)
        
        ##################
        # ACTIVITY IMAGE #
        ##################

        lat_lng_data = act_streams['latlng']
        normalised_route = norm_data(lat_lng_data)
        image_string = drw_route(normalised_route)
        api_key = 'a2bfa0b4f13fb01cec47fd7fa307ff8f'
        image_url = post_img(api_key, image_string)
        # image_url = 'test.png'

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
            is_commute=activity['is_commute'],
            start_lat=activity['start_lat'],
            start_lng=activity['start_lng'],
            end_lat=activity['end_lat'],
            end_lng=activity['end_lng'],
            name_id=activity['name']+'_'+str(activity['activity_id']),
            streams=act_streams_interpolated,
            maxs=rolling_dict,
            author=current_user)
        db.session.add(activity)
        db.session.commit()

    print(activities)

    # username = current_user.username
    # user = User.query.filter_by(username=username).first()
    # athlete_id = user.athlete_id

    # get_num_acts(access_token, athlete_id)

    location = "dashboards/7"
    embed_url = generate_embed_url(username, location)

    return render_template("index.html", user=user, embed_url=embed_url)

@app.route('/get_activity', methods = ['GET', 'POST'])
@login_required
def get_activity():
    if request.form:
        activity_id = request.form.get('activity_id')

    access_token = get_access_token()
    get_act(access_token, activity_id)

    username = current_user.username
    location = "dashboards/7"
    embed_url = generate_embed_url(username, location)

    return render_template("index.html", embed_url=embed_url)


@app.route('/delete', methods = ['GET', 'POST'])
@login_required
def delete():
    activities_delete = Activity.query.filter_by(author=current_user, activity_id="3257858588")
    for act in activities_delete:
        db.session.delete(act)
    db.session.commit()

    username = current_user.username
    location = "dashboards/7"
    embed_url = generate_embed_url(username, location)

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

    username = current_user.username
    location = "dashboards/7"
    embed_url = generate_embed_url(username, location)

    return render_template("index.html", user=user, embed_url=embed_url)

@app.route('/test', methods = ['GET', 'POST'])
def test():
    if request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        print(username)
        print(password)
    return render_template("test.html", filename='main.css')

def parse_request(req):
    """
    Parses application/json request body data into a Python dictionary
    """
    payload = req.get_data()
    # payload = unquote_plus(payload)
    # payload = re.sub('payload=', '', payload)
    payload = json.loads(payload)

    return payload

@app.route('/json_payload', methods = ['GET', 'POST'])
def json_payload():
    """
    Send a POST request to localhost:5000/json_payload with a JSON body with a "p" key
    to print that message in the server console
    """
    payload = parse_request(request)
    print(payload)
    return render_template("index.html")

@app.route('/slack', methods=['POST'])
def inbound():
    # if request.form.get('token') == SLACK_WEBHOOK_SECRET:
    if request.form:
        print('recieved!!!!')
        # channel = request.form.get('channel_name')
        # username = request.form.get('user_name')
        # text = request.form.get('text')
        # inbound_message = username + " in " + channel + " says: " + text
        # print(inbound_message)
    return Response(), 200
