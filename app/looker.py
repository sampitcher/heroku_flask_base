import looker_sdk
import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sdk = looker_sdk.init31("app/looker.ini", "PP")

# my_user = sdk.me()
# print(my_user)

# sql = '''
# SELECT current_date
# '''
# sql_query = looker_sdk.models.SqlQueryCreate(connection_name='strava',sql=sql)
# basic_table = sdk.create_sql_query(body=sql_query)
# query_slug = basic_table.slug

# query_result = sdk.run_sql_query(query_slug, 'json')
# print(query_result)

def get_activities():
    print('Getting Activites from Looker Model')
    look_result = sdk.run_look(5, 'json', apply_formatting=True)
    look_result = json.loads(look_result)
    return(look_result)