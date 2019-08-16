import requests
import json
import pandas as pd
# from google.cloud import bigquery
from pprint import pprint
import re
import datetime
# from google.cloud import storage
session = requests.Session()

client_id = '32114'
client_secret = '3f2de5d2888e942a24ca923125ca98752fce8dd1'
desired_scope = 'activity:read_all,profile:read_all,read_all'
redirect_host = 'https://localhost'

base_url = "https://www.strava.com/api/v3"
access_token = "13d8e59ea2b9c0d6559ec665ed5d8ae9f8e7c180"


# def set_up_auth(your_client_id,your_client_secret,your_desired_scope,your_redirect_host):
def set_up_auth():

    head = {'Authorization': 'Bearer {}'.format(access_token)}
    session.headers.update(head)

    auth_url = """https://www.strava.com/oauth/authorize?client_id={}&redirect_uri={}&response_type=code&scope={}""".format(client_id, redirect_host, desired_scope)
    print("Enter this URL into your browser and copy the code from the URL after you click authenicate")
    print(auth_url)
    return

# set_up_auth()

def auth_strava():
    head = {'Authorization': 'Bearer {}'.format(access_token)}
    session.headers.update(head)

    auth_url = """https://www.strava.com/oauth/authorize?client_id={}&redirect_uri={}&response_type=code&scope={}""".format(client_id, redirect_host, desired_scope)
    return(auth_url)


# code_old = "d122a57e196660808a4ebdb451d9a7f93000781a"
code = "6c9f0e1a12c202de122ac6ecc13b0d760c4489ce"


def get_activities(page_number,code, per_page=10):
    auth_url_2 = "https://www.strava.com/oauth/token?client_id={}&client_secret={}&code={}&grant_type=authorization_code".format(client_id, client_secret, code)

    r = session.post(auth_url_2)
    access_token = r.json()['access_token']
    session.headers.update({'Authorization': 'Bearer {}'.format(access_token)})

    r = session.get("{}/athlete/activities".format(base_url), params={'per_page': per_page, 'page': page_number})

    activities = r.json()

    # with open('activities2_{}.json'.format(page_number), 'w') as f:
        # f.write(json.dumps(activities))

    # pprint(activities)
    # return(len(activities))
    return(activities)

# get_activities(1)
# get_activity(2197549388)

# if __name__ == '__main__':
#     # n = get_activity_streams(2344637194)
#     # pprint(n['activities'])
#     # all_activities_to_csv()
#     get_activities(1,"a679a5b774c0ebe344c081c10a5ceaea03280ce8")

def get_park_run_activities(code):
    activity_array = []
    parkrun_array = []
    for i in range(10):
        data = get_activities(i+1,code, 200)
        for j in range(len(data)):
            activity_array.append(data[j])

    print(len(activity_array))

    for i in range(len(activity_array)):
        act_id = activity_array[i]['id']
        name = activity_array[i]['name']
        start_timestamp = activity_array[i]['start_date_local']
        act_type = activity_array[i]['type']
        distance = activity_array[i]['distance']
        elapsed_time = activity_array[i]['elapsed_time']
        moving_time = activity_array[i]['moving_time']
        start_date = re.search("(\d*-\d*-\d*)", start_timestamp).group()
        start_time = re.search("(\d*:\d*:\d*)", start_timestamp).group()
        timestamp_str = start_date+' '+start_time

        timetime = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        day_of_week = timetime.weekday()
        time = timetime.time()
        hour = time.hour
        minute = time.minute
        # print(timetime.weekday())

        activity_info_json = {}

        # print("{} {}".format(name, day_of_week))

        activity_info_json['act_id'] = act_id
        activity_info_json['name'] = name
        activity_info_json['day_of_week'] = day_of_week
        activity_info_json['time'] = time
        activity_info_json['start_timestamp'] = start_timestamp
        activity_info_json['act_type'] = act_type
        activity_info_json['distance'] = distance
        activity_info_json['elapsed_time'] = elapsed_time
        activity_info_json['moving_time'] = moving_time

        if day_of_week == 5 and act_type == 'Run' and distance > 4600 and distance < 5400:
            if hour == 8 and minute > 55:
                parkrun_array.append(activity_info_json)
            elif hour == 9 and minute < 15:
                parkrun_array.append(activity_info_json)
            else:
                None
        else:
            None

    # for i in range(len(parkrun_array)):
    #     print(parkrun_array[i])

    print(len(activity_array))
    print(activity_array)
    return(parkrun_array)

def get_activity(activity_id,code):
    auth_url_2 = "https://www.strava.com/oauth/token?client_id={}&client_secret={}&code={}&grant_type=authorization_code".format(client_id, client_secret, code)

    r = session.post(auth_url_2)
    access_token = r.json()['access_token']
    session.headers.update({'Authorization': 'Bearer {}'.format(access_token)})

    r = session.get("{}/activities/{}".format(base_url, activity_id))

    activity = r.json()

    # with open('activity_{}.json'.format(activity_id), 'w') as f:
        # f.write(json.dumps(activity))

    # pprint(activity)
    # return(len(activity))
    return(activity)

# get_activities(1)
# get_activity(2197549388)


def get_activity_laps(activity_id):
    auth_url_2 = "https://www.strava.com/oauth/token?client_id={}&client_secret={}&code={}&grant_type=authorization_code".format(client_id, client_secret, code)

    r = session.post(auth_url_2)
    access_token = r.json()['access_token']
    session.headers.update({'Authorization': 'Bearer {}'.format(access_token)})

    r = session.get("{}/activities/{}/laps".format(base_url, activity_id))

    activities = r.json()

    # with open('activitiess.json', 'w') as f:
    #   f.write(json.dumps(activities))

    pprint(activities)
    return activities


def get_activity_streams_raw(activity_id):
    auth_url_2 = "https://www.strava.com/oauth/token?client_id={}&client_secret={}&code={}&grant_type=authorization_code".format(client_id, client_secret, code)

    r = session.post(auth_url_2)
    access_token = r.json()['access_token']
    session.headers.update({'Authorization': 'Bearer {}'.format(access_token)})

    r = session.get("{}/activities/{}/streams?keys=time,altitude,watts,latlng,heartrate&key_by_type=true".format(base_url, activity_id))

    activities = r.json()

    # with open('activitiess.json', 'w') as f:
    #   f.write(json.dumps(activities))

    return activities


def get_activity_streams(activity_id,code):
    auth_url_2 = "https://www.strava.com/oauth/token?client_id={}&client_secret={}&code={}&grant_type=authorization_code".format(client_id, client_secret, code)

    r = session.post(auth_url_2)
    access_token = r.json()['access_token']
    session.headers.update({'Authorization': 'Bearer {}'.format(access_token)})

    r = session.get("{}/activities/{}/streams?keys=time,altitude,watts,latlng,heartrate&key_by_type=true".format(base_url, activity_id))

    activity_streams = r.json()

    bigquery_array = []
    map_array = []
    new_dict = {}

    # with open('activitiess.json', 'r') as f:
    #   activity_streams = json.loads(f.read())

    data_points = activity_streams['distance']['original_size']
    # data_points = 200
    # print(data_points)

    null_data = []
    null_array_data = []
    for i in range(data_points):
        null_data.append(0)
        null_array_data.append([0, 0])

    try:
        time_data = activity_streams["time"]["data"]
    except:
        time_data = null_data

    try:
        distance_data = activity_streams["distance"]["data"]
    except:
        distance_data = null_data

    try:
        latlng_data = activity_streams["latlng"]["data"]
    except:
        latlng_data = null_array_data

    try:
        alt_data = activity_streams["altitude"]["data"]
    except:
        alt_data = null_data

    try:
        heartrate_data = activity_streams["heartrate"]["data"]
    except:
        heartrate_data = null_data

    try:
        cadence_data = activity_streams["cadence"]["data"]
    except:
        cadence_data = null_data

    try:
        watts_data = activity_streams["watts"]["data"]
    except:
        watts_data = null_data

    try:
        moving_data = activity_streams["moving"]["data"]
    except:
        moving_data = null_data

    for i in range(data_points):
        bigquery_array.append({"id": i + 1, "time": time_data[i], "distance": distance_data[i], "lat": latlng_data[i][0], "lon": latlng_data[i][1], "altitude": alt_data[i], "heartrate": heartrate_data[i], "cadence": cadence_data[i], "watts": watts_data[i], "moving": moving_data[i]})
        map_array.append({"lat_1": latlng_data[i][0], "lng_1": latlng_data[i][1], "lat_2": latlng_data[i - 1][0], "lng_2": latlng_data[i - 1][1]})

    new_dict["activity_id"] = activity_id
    new_dict["activities"] = bigquery_array
    new_dict["lat_lngs"] = map_array

    with open('activity_streams.json', 'w') as f:
        f.write(json.dumps(new_dict))

    return(new_dict)


# def get_activity_streams(activity_id):
#   auth_url_2 = "https://www.strava.com/oauth/token?client_id={}&client_secret={}&code={}&grant_type=authorization_code".format(client_id, client_secret, code)

#   r = session.post(auth_url_2)
#   access_token = r.json()['access_token']
#   session.headers.update({'Authorization': 'Bearer {}'.format(access_token)})

#   r = session.get("{}/activities/{}/streams?keys=time,distance,latlng,altitude,heartrate,cadence,watts,moving&key_by_type=true".format(base_url,activity_id))

#   activities = r.json()

#   # with open('activitiess.json', 'w') as f:
#   #   f.write(json.dumps(activities))

#   return activities
def json_to_csv(index_number):
    with open('activities_1.json', 'r') as f:
        activities = json.loads(f.read())

    new_dict = {}
    ix = 1
    for i in range(len(activities)):
        new_dict[ix] = activities[i]
        ix += 1

    df = pd.DataFrame.from_dict(new_dict, orient='index')
    file_name = 'activities{}.csv'.format(index_number)
    df.to_csv(file_name)
    return

# json_to_csv(1)


def json_to_csv_all(file_count):
    activities_dict = {}
    ix = 1

    for i in range(file_count):
        with open('activities_{}.json'.format(i + 1), 'r') as f:
            activities = json.loads(f.read())

        for i in range(len(activities)):
            activities_dict[ix] = activities[i]
            ix += 1

    df = pd.DataFrame.from_dict(activities_dict, orient='index')
    file_name = 'activities_all.csv'
    df.to_csv(file_name)
    return

# json_to_csv_all(5)


def activity_id_list_query():
    client = bigquery.Client()
    query = (
        'SELECT id, start_date FROM `strava-project-226316.strava_dataset.strava_activities` ORDER BY start_date desc LIMIT 20'
    )
    query_job = client.query(query)  # API request - starts the query
    query_list = []
    bigquery_dump = []

    for row in query_job:
        query_list.append(row[0])
        print(row[0])

    for i in range(len(query_list)):
        add = get_activity_streams(query_list[i])
        bigquery_dump.append(add)

    print(bigquery_dump)

    with open('activity_streams_dump.json', 'w') as f:
        f.write(json.dumps(bigquery_dump))


def get_segments():
    bounds = [50.925162, -0.680935, 50.793178, -0.293204]
    activity_type = 'riding'
    auth_url_2 = "https://www.strava.com/oauth/token?client_id={}&client_secret={}&code={}&grant_type=authorization_code".format(client_id, client_secret, code)

    r = session.post(auth_url_2)
    access_token = r.json()['access_token']
    session.headers.update({'Authorization': 'Bearer {}'.format(access_token)})

    r = session.get("{}/segments/explore?bounds={}&activity_type={}".format(base_url, bounds, activity_type))

    activities = r.json()

    pprint(activities)

    with open('segments.json', 'w') as f:
        f.write(json.dumps(activities))

    # print(r)
    return(len(activities))

def get_all_activities(page_number,per_page):
    auth_url_2 = "https://www.strava.com/oauth/token?client_id={}&client_secret={}&code={}&grant_type=authorization_code".format(client_id, client_secret, code)
    # page_number = 1
    # per_page = 5

    r = session.post(auth_url_2)
    access_token = r.json()['access_token']
    session.headers.update({'Authorization': 'Bearer {}'.format(access_token)})

    r = session.get("{}/athlete/activities".format(base_url), params={'per_page': per_page, 'page': page_number})

    activities = r.json()

    # print(activities[1]['id'])

    with open('activities_new_{}.json'.format(page_number), 'w') as f:
        f.write(json.dumps(activities))

    pprint(activities)
    # return(len(activities))

def get_all_activities_to_csv():
    auth_url_2 = "https://www.strava.com/oauth/token?client_id={}&client_secret={}&code={}&grant_type=authorization_code".format(client_id, client_secret, code)
    page_number = 1
    per_page = 2

    r = session.post(auth_url_2)
    access_token = r.json()['access_token']
    session.headers.update({'Authorization': 'Bearer {}'.format(access_token)})

    r = session.get("{}/athlete/activities".format(base_url), params={'per_page': per_page, 'page': page_number})

    activities = r.json()

    print(activities[1]['id'])

    with open('activities_{}.json'.format(page_number), 'w') as f:
        f.write(json.dumps(activities))

    pprint(activities)
    # return(len(activities))


def all_activities_to_csv():
    all_activities_dict = {}
    temp_array = []
    k = 1

    try:
        for i in range(10):
            with open('activities_new_{}.json'.format(i+1), 'r') as f:
                activities = json.loads(f.read())
    
            # print(activities)
            
            for j in range(200):
                temp_dict = {}
                temp_dict['id'] = activities[j]['id']
                temp_dict['name'] = activities[j]['name']
                temp_dict['athlete'] = activities[j]['athlete']['id']
                # temp_dict['average_cadence'] = activities[j]['average_cadence']
                temp_dict['has_heartrate'] = activities[j]['has_heartrate']
                has_hr = activities[j]['has_heartrate']
                if has_hr == True:
                    temp_dict['average_heartrate'] = activities[j]['average_heartrate']
                else:
                    temp_dict['average_heartrate'] = 0
                temp_dict['average_speed'] = activities[j]['average_speed']
                # temp_dict['average_watts'] = activities[j]['average_watts']
                # temp_dict['commute'] = activities[j]['commute']
                # temp_dict['device_watts'] = activities[j]['device_watts']
                temp_dict['distance'] = activities[j]['distance']
                temp_dict['elapsed_time'] = activities[j]['elapsed_time']
                # temp_dict['elev_high'] = activities[j]['elev_high']
                # temp_dict['elev_low'] = activities[j]['elev_low']
                # temp_dict['external_id'] = activities[j]['external_id']
                temp_dict['gear_id'] = activities[j]['gear_id']
                # temp_dict['heartrate_opt_out'] = activities[j]['heartrate_opt_out']
                # temp_dict['kilojoules'] = activities[j]['kilojoules']
                if has_hr == True:
                    temp_dict['max_heartrate'] = activities[j]['max_heartrate']
                else:
                    temp_dict['max_heartrate'] = 0
                temp_dict['max_speed'] = activities[j]['max_speed']
                # temp_dict['max_watts'] = activities[j]['max_watts']
                temp_dict['moving_time'] = activities[j]['moving_time']
                temp_dict['name'] = activities[j]['name']
                temp_dict['start_date'] = activities[j]['start_date']
                # temp_dict['start_latitude'] = activities[j]['start_latitude']
                # temp_dict['start_longitude'] = activities[j]['start_longitude']
                # temp_dict['start_latlng'] = activities[j]['start_latlng']
                # temp_dict['end_latlng'] = activities[j]['end_latlng']
                temp_dict['suffer_score'] = activities[j]['suffer_score']
                # temp_dict['total_elevation_gain'] = activities[j]['total_elevation_gain']
                temp_dict['type'] = activities[j]['type']
                # temp_dict['weighted_average_watts'] = activities[j]['weighted_average_watts']
                # temp_dict['workout_type'] = activities[j]['workout_type']

                all_activities_dict[k] = temp_dict
                k = k+1

                temp_array.append(activities[j]['id'])
                # print(len(temp_array))
                # print(activities[j]['id'])
    except:
        x=1
    # print(len(temp_array))
    # pprint(all_activities_dict)
    # print(len(all_activities_dict))

    with open('all_activities.json', 'w') as f:
        f.write(json.dumps(all_activities_dict))

    df = pd.DataFrame.from_dict(all_activities_dict, orient='index')
    file_name = 'all_activities_070519.csv'
    df.to_csv(file_name)

    return file_name

def new_activities_to_csv():
    x=1










