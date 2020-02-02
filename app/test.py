import datetime

date_old = '2016-08-23T11:52:33Z'

date_new = datetime.datetime.strptime(date_old, '%Y-%m-%dT%H:%M:%SZ').strftime('%s')
# date_new = date_new.strftime('%s')

print(date_new)