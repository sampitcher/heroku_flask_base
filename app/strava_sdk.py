import requests
import json
from pprint import pprint
import time
import datetime

session = requests.Session()

client_id = '32114'
client_secret = '3f2de5d2888e942a24ca923125ca98752fce8dd1'
desired_scope = 'activity:read_all,profile:read_all,read_all'
redirect_host = 'https://localhost'

base_url = "https://www.strava.com/api/v3"
app_access_token = "13d8e59ea2b9c0d6559ec665ed5d8ae9f8e7c180"

# code = "6c9f0e1a12c202de122ac6ecc13b0d760c4489ce"

def set_up_auth():

    head = {'Authorization': 'Bearer {}'.format(app_access_token)}
    session.headers.update(head)

    auth_url = """https://www.strava.com/oauth/authorize?client_id={}&redirect_uri={}&response_type=code&scope={}""".format(client_id, redirect_host, desired_scope)
    print("Enter this URL into your browser and copy the code from the URL after you click authenicate")
    print(auth_url)
    return

# set_up_auth()

# code = "e6544b470f32e024d0c2d9aac3fb09a1be91a480"
# code = "9995da9c388571e3960e663b018251c282c9d7b7"

def get_tokens_with_code(code):
    auth_url_2 = "https://www.strava.com/oauth/token?client_id={}&client_secret={}&code={}&grant_type=authorization_code".format(client_id, client_secret, code)

    r = session.post(auth_url_2)
    access_token = r.json()['access_token']
    refresh_token = r.json()['refresh_token']
    expires_at = r.json()['expires_at']

    return(access_token, refresh_token, expires_at)

# access_token, refresh_token, expires_at = get_tokens_with_code(code)
# print(access_token)
# print(refresh_token)
# print(expires_at)
# access_token = "eed5d24b524b46e824c5aa7f7e53653495ca284d"
# refresh_token = "ce0108090e8a4b7f9be7a1493c40458deeb2d229"

def get_tokens_with_refresh_token(refresh_token):
    auth_url_2 = "https://www.strava.com/oauth/token?client_id={}&client_secret={}&refresh_token={}&grant_type=refresh_token".format(client_id, client_secret, refresh_token)

    r = session.post(auth_url_2)
    access_token = r.json()['access_token']
    refresh_token = r.json()['refresh_token']
    expires_at = r.json()['expires_at']

    return(access_token, refresh_token, expires_at)

# access_token, refresh_token = get_tokens_with_refresh_token(refresh_token)



def get_athlete_id(access_token):
    auth_url_2 = "https://www.strava.com/oauth/token?client_id={}&client_secret={}".format(client_id, client_secret)

    r = session.post(auth_url_2)
    session.headers.update({'Authorization': 'Bearer {}'.format(access_token)})

    print(f'Getting athlete information from Strava')
    r = session.get("{}/athlete".format(base_url))

    athlete_info_raw = r.json()
    athlete_id = athlete_info_raw['id']

    print(athlete_id)

    return(athlete_id)

def get_num_of_activities(access_token, athlete_id):
    auth_url_2 = "https://www.strava.com/oauth/token?client_id={}&client_secret={}".format(client_id, client_secret)

    r = session.post(auth_url_2)
    session.headers.update({'Authorization': 'Bearer {}'.format(access_token)})

    print(f'Getting athlete information from Strava')
    r = session.get("{}/athletes/{}/stats".format(base_url, athlete_id))

    athlete_stats_raw = r.json()

    print(athlete_stats_raw)

    return(athlete_stats_raw)

def get_activities(access_token, max_time=0):
    if max_time is None:
        max_time = 0

    auth_url_2 = "https://www.strava.com/oauth/token?client_id={}&client_secret={}".format(client_id, client_secret)

    r = session.post(auth_url_2)
    session.headers.update({'Authorization': 'Bearer {}'.format(access_token)})

    activities_array = []
    print(f'Getting activities from Strava')
    r = session.get("{}/athlete/activities".format(base_url), params={'after': max_time, 'per_page': 1, 'page': 1})

    activities_raw = r.json()

    for i in range(1):
        try:
            print(f'Getting Activity number {i + 1}')
            activities_array.append(clean_raw_activities(activities_raw[i]))
        except:
            pass

        print(activities_array)
    return(activities_array)

def get_activity(access_token, activity_id):

    auth_url_2 = "https://www.strava.com/oauth/token?client_id={}&client_secret={}".format(client_id, client_secret)

    r = session.post(auth_url_2)
    session.headers.update({'Authorization': 'Bearer {}'.format(access_token)})

    print(f'Getting activity from Strava')
    r = session.get(f"{base_url}/activities/{activity_id}")

    activity_raw = r.json()

    activity = clean_raw_activities(activity_raw)

    print('Raw Activity json:')
    print(activity_raw)
    print('----')
    print('Cleaned Activity json:')
    print(activity)

    return(activity)

def get_activity_streams(access_token, activity_id):

    auth_url_2 = "https://www.strava.com/oauth/token?client_id={}&client_secret={}".format(client_id, client_secret)

    r = session.post(auth_url_2)
    session.headers.update({'Authorization': 'Bearer {}'.format(access_token)})

    keys = ["time", "latlng", "distance", "altitude", "velocity_smooth", "heartrate", "cadence", "watts", "temp", "moving", "grade_smooth"]
    activity_streams = {}
    
    for key in keys:
        print(f"\nGetting activity streams from Strava for {key}")
        r = session.get(f"{base_url}/activities/{activity_id}/streams", params={'keys': [key]})
        activity_streams_raw = r.json()
        original_size = activity_streams_raw[0]['original_size']

        for i in range(len(activity_streams_raw)):
            if activity_streams_raw[i]['type'] == key:
                activity_streams[key] = activity_streams_raw[i]['data']
                pass
            elif len(activity_streams_raw) < 2:
                activity_streams[key] = [None] * original_size
                pass
        try:
            print(activity_streams[key][:6])
        except:
            print('Not enough rows...')

    activity_streams['time_key'] = activity_streams['time']
    activity_streams['original'] = [True] * original_size
    activity_streams['latlng'][0] = None
    activity_streams['latlng'][-1] = None
    
    # print(activity_streams)
    return(activity_streams)

def get_activity_laps(access_token, activity_id):

    auth_url_2 = "https://www.strava.com/oauth/token?client_id={}&client_secret={}".format(client_id, client_secret)

    r = session.post(auth_url_2)
    session.headers.update({'Authorization': 'Bearer {}'.format(access_token)})

    print(f'Getting activity from Strava')
    r = session.get(f"{base_url}/activities/{activity_id}/laps")

    activity_laps_raw = r.json()

    # activity = clean_raw_activities(activity_laps_raw)

    # print('Raw Activity json:')
    # print(activity_laps_raw)
    # print('----')
    # print('Cleaned Activity json:')
    # print(activity)
    for i in activity_laps_raw:
        print(i)

    # return(activity)
    pass

def clean_raw_activities(i):
    timenow = time.time()
    activity_id = i['id']
    name = i['name']
    activity_type = i['type']
    timestamp = i['start_date']
    epoch = int(datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ').strftime('%s'))
    user_id = i['athlete']['id']
    elevation = i['total_elevation_gain']
    distance = i['distance']
    duration = i['moving_time']
    is_commute = i['commute']

    try:
        start_lat = i['start_latlng'][0]
        start_lng = i['start_latlng'][1]
        end_lat = i['end_latlng'][0]
        end_lng = i['end_latlng'][1]
    except:
        start_lat = 0
        start_lng = 0
        end_lat = 0
        end_lng = 0

    try:
        max_speed = i['max_speed']
    except:
        max_speed = 0
    try:
        avg_speed = i['avg_speed']
    except:
        avg_speed = 0

    try:
        max_power = i['max_power']
    except:
        max_power = 0
    try:
        avg_power = i['avg_power']
    except:
        avg_power = 0

    try:
        max_heartrate = i['max_heartrate']
    except:
        max_heartrate = 0
    try:
        avg_heartrate = i['avg_heartrate']
    except:
        avg_heartrate = 0

    activity = {
        "activity_id": activity_id,
        "name": name,
        "activity_type": activity_type,
        "epoch": epoch,
        "timenow": timenow,
        "timestamp": timestamp,
        "user_id": user_id,
        "elevation": elevation,
        "distance": distance,
        "duration": duration,
        "max_speed": max_speed,
        "avg_speed": avg_speed,
        "max_power": max_power,
        "avg_power": avg_power,
        "max_heartrate": max_heartrate,
        "avg_heartrate": avg_heartrate,
        "is_commute": is_commute,
        "start_lat": start_lat,
        "start_lng": start_lng,
        "end_lat": end_lat,
        "end_lng": end_lng
    }

    return(activity)