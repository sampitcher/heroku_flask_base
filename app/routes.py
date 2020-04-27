from flask import render_template, flash, redirect, url_for, request, make_response, Response
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Activity, Mappa
import pandas as pd
import numpy as np
import time
import json

from app.strava_sdk import get_tokens_with_code as get_tokens_w_c, get_tokens_with_refresh_token as get_tokens_w_rt, get_activities as get_acts, get_athlete_id as get_ath_id, get_num_of_activities as get_num_acts, get_activity as get_act, get_activity_streams as get_act_streams, get_activity_laps as get_act_laps
from app.pbl import get_embed_user as pbl_get_user, generate as pbl_generate
from app.imager import normalise_data as norm_data, draw_route as drw_route, draw_elevation as drw_elevation, post_image_str as post_img, post_image_file as post_img_file
# from app.looker import get_activities as get_act_looker

##################
# BASE FUNCTIONS #
##################

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

def delete_activity(activity_id=None):
    if activity_id == None:
        print('No Activity ID...')
        return True
    else:
        print(f'Deleting activity using Activity ID: {activity_id}')
    
    activities_delete = Activity.query.filter_by(author=current_user, activity_id=activity_id)
    for act in activities_delete:
        db.session.delete(act)
    db.session.commit()
    return True

def sync_activities(activity_id=None):
    username = current_user.username
    user = User.query.filter_by(username=username).first()
    user_id = user.id
    access_token = get_access_token()
    print(f'user id: {user_id}')

    if activity_id == None:
        print('Getting activities using epoch as max time')
        # Find the latest activity epoch in database
        max_epoch = db.session.query(db.func.max(Activity.epoch)).filter(Activity.user_id == user_id).scalar()
        print(f'Last epoch: {max_epoch}')
        # Get an array of 1 activities (when writing it's only one activity)
        activities = get_acts(access_token, max_epoch)
    else:
        print(f'Getting activity using Activity ID: {activity_id}')
        activities = get_act(access_token, activity_id)

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
            rolling_avg = df_final.rolling(i, win_type='triang').mean()
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
        
        print(rolling_dict)
        for i in rolling_dict:
            print(f'{i}: {rolling_dict[i]}')
            try:
                if rolling_dict[i] >= 0:
                    pass
                else:
                    rolling_dict[i] = None
            except:
                rolling_dict[i] = None
        
        #################################
        # ACTIVITY AND ELEVATION IMAGES #
        #################################

        lat_lng_data = act_streams['latlng']
        normalised_route = norm_data(lat_lng_data)
        image_string = drw_route(normalised_route)
        api_key = 'a2bfa0b4f13fb01cec47fd7fa307ff8f'
        image_url = post_img(api_key, image_string)

        distance_data = act_streams['distance']
        altitude_data = act_streams['altitude']
        ys = [0]*len(distance_data)
        elevation_image_string = drw_elevation(distance_data, altitude_data, ys)
        elevation_image_url = post_img(api_key, elevation_image_string)

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
            icon_url=image_url,
            altitude_url=elevation_image_url,
            author=current_user)
        db.session.add(activity)
        db.session.commit()

    if activity_id == None:
        print('Added latest activities')
    else:
        print(f'Synced Activity {activity_id}')

    # location = "dashboards/7"
    # embed_url = generate_embed_url(username, location)

    # return render_template("index.html", user=user, embed_url=embed_url)
    return True

def update_activity(activity_id=None):
    if activity_id == None:
        print('No Activity ID...')
        return True
    else:
        delete_activity(activity_id)
        sync_activities(activity_id)
        print(f'Updated Activity ID {activity_id}')
        return True

###############
# BASE ROUTES #
###############

@app.route('/')

@app.route('/index')
@login_required
def index():
    # username = current_user.username
    # location = "dashboards/7"
    # embed_url = generate_embed_url(username, location)
    # resp = make_response(render_template('index.html', title='Home', embed_url=embed_url))
    # resp.headers.add('Access-Control-Allow-Origin', 'http://pitcherpakeman001.lookersandbox.com')
    # resp.headers.add('Access-Control-Allow-Credentials', 'true')
    # resp.set_cookie('strava-pitcherpakeman-test', value='this is a test', domain=".lookersandbox.com", samesite=None)
    # print(resp)
    # return resp
    return redirect(url_for('activities'))

#######################
# USER SIGN-IN ROUTES #
#######################

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

##################
# STRAVA ROUTES  #
##################

@app.route('/sync', methods = ['GET', 'POST'])
@login_required
def sync():
    sync_activities()

    username = current_user.username
    # location = "dashboards/7"
    # embed_url = generate_embed_url(username, location)

    # return render_template("activities.html", user=user, embed_url=embed_url)
    return redirect(url_for('activities'))

@app.route('/sync_activity_id', methods = ['GET', 'POST'])
@login_required
def sync_activity_id():
    username = current_user.username
    if request.form:
        activity_id = request.form.get('activity_id')
        print(f'User selected to add the Activity ID: {activity_id}')
        # access_token = get_access_token()
    
    sync_activities(activity_id)

    location = "dashboards/7"
    embed_url = generate_embed_url(username, location)

    return render_template("index.html", user=user, embed_url=embed_url)

@app.route('/delete_activity_id', methods = ['GET', 'POST'])
@login_required
def delete_activity_id():
    if request.form:
        activity_id = request.form.get('activity_id')
        print(f'User selected to delete the Activity ID: {activity_id}')
        delete_activity(activity_id)
    
    username = current_user.username
    location = "dashboards/7"
    embed_url = generate_embed_url(username, location)

    return render_template("index.html", user=user, embed_url=embed_url)


@app.route('/update_activity_id', methods = ['GET', 'POST'])
@login_required
def update_activity_id():
    if request.form:
        activity_id = request.form.get('activity_id')
        print(f'User selected to delete the Activity ID: {activity_id}')
        update_activity(activity_id)
    
    username = current_user.username
    location = "dashboards/7"
    embed_url = generate_embed_url(username, location)

    return render_template("index.html", user=user, embed_url=embed_url)


@app.route('/activities', methods = ['GET', 'POST'])
@login_required
def activities():
    # USE LOOKER API TO RETURN RESULTS OF STRAVA ACTIVITES LOOK 5
    if request.form:
        try:
            activity_id_update = request.form.get('activity_id_update')
            print(activity_id_update)
            update_activity(activity_id_update)
        except:
            pass

        try:
            activity_id_delete = request.form.get('activity_id_delete')
            print(activity_id_delete)
            delete_activity(activity_id_delete)
        except:
            pass
        
        try:
            activity_id_sync = request.form.get('activity_id_sync')
            print(activity_id_sync)
            sync_activities(activity_id_sync)
        except:
            pass
    
    username = current_user.username
    user = User.query.filter_by(username=username).first()
    user_id = user.id
    activities_sql = db.session.query(
        Activity.epoch,
        Activity.timestamp,
        Activity.activity_id,
        Activity.icon_url,
        Activity.name,
        Activity.activity_type,
        Activity.is_commute,
        Activity.duration,
        Activity.distance,
        Activity.altitude_url
        ).filter(Activity.user_id == user_id).order_by(Activity.epoch.desc()).limit(100).all()
    print(activities_sql)
    look_activities = []
    for u in activities_sql:
        distance = float(u[8])
        distance_km = str(round(1.0 * distance / 1000, 2)) + ' km'

        duration = float(u[7])
        duration_hhmmss = time.strftime('%H:%M:%S', time.gmtime(duration))

        temp_dict = {
            "epoch": u[0],
            "activity_date": u[1],
            "activity_id": u[2],
            "icon_url": u[3],
            "name": u[4],
            "type": u[5],
            "is_commute": u[6],
            "duration": duration_hhmmss,
            "distance": distance_km,
            "altitude_url": u[9]
        }
        print(temp_dict)
        look_activities.append(temp_dict)
    print(look_activities)

    return render_template("activities.html", look_activities=look_activities)


@app.route('/mappa', methods = ['GET', 'POST'])
@login_required
def mappa():
    username = current_user.username
    user = User.query.filter_by(username=username).first()
    user_id = user.id

    if request.form.get('activity_id_mappa') != None:
        activity_id_mappa = request.form.get('activity_id_mappa')
        print(activity_id_mappa)

        activities_sql = db.session.query(
            Activity.activity_id,
            Activity.icon_url,
            Activity.name,
            Activity.duration,
            Activity.distance,
            Activity.altitude_url,
            Activity.max_speed,
            Activity.avg_speed,
            Activity.max_power,
            Activity.avg_power,
            Activity.max_heartrate,
            Activity.avg_heartrate
            ).filter(
                Activity.user_id == user_id,
                Activity.activity_id == activity_id_mappa
                ).all()
        icon_url = activities_sql[0][1]
        name = activities_sql[0][2]
        # duration = 'Duration: '+str(time.strftime('%H:%M:%S', str(time.gmtime(int(activities_sql[0][3])))))
        duration_raw = activities_sql[0][3]
        duration = str(time.strftime('%H:%M:%S', time.gmtime(int(duration_raw))))
        distance = str(round(float(activities_sql[0][4]) / 1000, 2))+' km'
        altitude_url = activities_sql[0][5]
        max_speed = str(round(float(activities_sql[0][6]) * 3.6, 2))+' km/h'
        avg_speed = str(round(float(activities_sql[0][7]) * 3.6, 2))+' km/h'
        max_power = str(activities_sql[0][8])+' watts'
        avg_power = str(activities_sql[0][9])+' watts'
        max_heartrate = str(round(float(activities_sql[0][10]),0))[:-2]+' bpm'
        avg_heartrate = str(round(float(activities_sql[0][11]),0))[:-2]+' bpm'

        mappa_image = Mappa(
            activity_id=activity_id_mappa,
            name=name,
            epoch=time.time(),
            user_id=user_id,
            icon_url=icon_url,
            altitude_url=altitude_url,
            max_speed = max_speed,
            avg_speed = avg_speed,
            distance = distance,
            duration = duration,
            max_power = max_power,
            avg_power = avg_power,
            max_heartrate = max_heartrate,
            avg_heartrate = avg_heartrate)
        db.session.add(mappa_image)
        db.session.commit()

        response = make_response(render_template('mappa.html',
        title='Mappa',
        icon_url=icon_url,
        name=name,
        duration=duration,
        distance=distance,
        altitude_url=altitude_url,
        max_speed = max_speed,
        avg_speed = avg_speed,
        max_power = max_power,
        avg_power = avg_power,
        max_heartrate = max_heartrate,
        avg_heartrate = avg_heartrate))
        return response
    
    if request.method == 'POST':
        f = request.files['file']
        api_key = 'a2bfa0b4f13fb01cec47fd7fa307ff8f'
        background_url = post_img_file(api_key, f)

        mappa_sql = db.session.query(
            Mappa.activity_id,
            Mappa.icon_url,
            Mappa.name,
            Mappa.altitude_url,
            Mappa.max_speed,
            Mappa.avg_speed,
            Mappa.max_power,
            Mappa.avg_power,
            Mappa.max_heartrate,
            Mappa.avg_heartrate,
            Mappa.duration,
            Mappa.distance
            ).order_by(Mappa.epoch.desc()).limit(1).all()
        activity_id = mappa_sql[0][0]
        icon_url = mappa_sql[0][1]
        name = mappa_sql[0][2]
        altitude_url = mappa_sql[0][3]
        max_speed = mappa_sql[0][4]
        avg_speed = mappa_sql[0][5]
        max_power = mappa_sql[0][6]
        avg_power = mappa_sql[0][7]
        max_heartrate = mappa_sql[0][8]
        avg_heartrate = mappa_sql[0][9]
        duration = mappa_sql[0][10]
        distance = mappa_sql[0][11]
        response = make_response(render_template('mappa.html',
        title='Mappa',
        icon_url=icon_url,
        name=name,
        duration=duration,
        distance=distance,
        altitude_url=altitude_url,
        max_speed = max_speed,
        avg_speed = avg_speed,
        max_power = max_power,
        avg_power = avg_power,
        max_heartrate = max_heartrate,
        avg_heartrate = avg_heartrate,
        background_url=background_url))
        return response
    
    response = make_response(render_template('mappa.html',
    title='Mappa',
    icon_url='',
    name='',
    duration='',
    distance='',
    altitude_url=''))
    return response


@app.route('/commute_ml')
@login_required
def commute_ml():
    response = make_response(render_template('commute_ml.html', title='Commute ML'))
    return response


@app.route('/get_activity', methods = ['GET', 'POST'])
@login_required
def get_activity():
    if request.form:
        activity_id = request.form.get('activity_id')
        # update_activity(activity_id)
        print(activity_id)

    access_token = get_access_token()
    get_act(access_token, activity_id)

    username = current_user.username
    location = "dashboards/7"
    embed_url = generate_embed_url(username, location)

    return render_template("index.html", embed_url=embed_url)


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


@app.route('/activity_stats', methods=['GET', 'POST'])
@login_required
def activity_stats():
    act_streams = ''
    icon_image_url = ''
    username = current_user.username
    if request.form:
        activity_id = request.form.get('activity_id')
        print(activity_id)
        access_token = get_access_token()
        act_streams = get_act_streams(access_token, activity_id)
        # print(act_streams['latlng'])

        # lat_lng_data = act_streams['latlng']
        # normalised_route = norm_data(lat_lng_data)
        # icon_image_string = drw_route(normalised_route)
        # api_key = 'a2bfa0b4f13fb01cec47fd7fa307ff8f'
        # icon_image_url = post_img(api_key, icon_image_string)

        distance_data = act_streams['distance']
        altitude_data = act_streams['altitude']
        ys = [0]*len(distance_data)
        icon_image_string = drw_elevation(distance_data, altitude_data, ys)
        api_key = 'a2bfa0b4f13fb01cec47fd7fa307ff8f'
        icon_image_url = post_img(api_key, icon_image_string)

    response = make_response(render_template('activity_stats.html', title='Activity Stats', act_streams=act_streams, icon_image_url=icon_image_url))
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