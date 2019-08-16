from app.strava_api import get_activities as gatcs, get_activity_streams as gas, get_activity as gact
# from pprint import pprint
from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
import time
from pprint import pprint
import io
from flask import Flask, render_template, request, redirect
from PIL import Image, ImageFont, ImageDraw
from flask_login import current_user

code = "6c9f0e1a12c202de122ac6ecc13b0d760c4489ce"

# VARIABLES
# activity_id = 2271908329

# base_image_location = 'bike_photo.jpg'

# TEXT BOX SIZE
xa1, xb1 = 625, 970
ya1, yb1 = 575, 845

def clear_photo():
	base_image = Image.open('white.png')
	basewidth = 1000
	wpercent = (basewidth/float(base_image.size[0]))
	hsize = int((float(base_image.size[1])*float(wpercent)))
	base_image = base_image.resize((basewidth,hsize), Image.ANTIALIAS)
	base_image.save('static/base_image_final.png')

def get_data(activity_id,code):
	data = gas(activity_id,code)['activities']
	activity_info = gact(activity_id,code)

	# VARIABLES

	name = activity_info['name']
	name_string = str(name)

	distance = activity_info['distance']
	distancekm = round(distance/1000,1)
	distance_string = "{} km".format(str(distancekm))

	elev_high = activity_info['elev_high']
	elev_low = activity_info['elev_low']
	elevation = str(round(elev_high - elev_low,1))
	elevation_string = "{} m".format(str(elevation))

	duration = activity_info['moving_time']
	duration_formatted = time.strftime('%Hh%M', time.gmtime(duration))
	duration_string = str(duration_formatted)

	max_speed = round(activity_info['max_speed']*3.6,1)
	max_speed_string = "{} kph".format(str(max_speed))

	avg_speed = round(activity_info['average_speed']*3.6,1)
	avg_speed_string = "{} kph".format(str(avg_speed))

	# max_power = str(activity_info[]
	# avg_power = str(activity_info[]
	max_power_string = '560 watts'
	avg_power_string = '231 watts'

	xaxis = []
	yaxis = []
	y2axis = []
	lat = []
	lon = []

	for i in data:
		xaxis.append(i['distance'])
		yaxis.append(i['altitude'])
		y2axis.append(-700)
		lat.append(i['lat'])
		lon.append(i['lon'])

	# pprint(max_speed)
	return(name_string, distance_string, elevation_string, duration_string, max_speed_string, avg_speed_string, max_power_string, avg_power_string, xaxis, yaxis, y2axis, lat, lon)
	# print(name_string, distance_string, elevation_string, duration_string, max_speed_string, avg_speed_string, max_power_string, avg_power_string, xaxis, yaxis, y2axis, lat, lon)


# get_data(2381033549)

def print_activity(activity_id):
	new_dict = gas(activity_id,code)
	# pprint(new_dict)

# def create_base_image(base_image_location):
# 	base_image = Image.open(base_image_location)

# 	# Resize the image

# 	basewidth = 1000
# 	wpercent = (basewidth/float(base_image.size[0]))
# 	hsize = int((float(base_image.size[1])*float(wpercent)))
# 	base_image = base_image.resize((basewidth,hsize), Image.ANTIALIAS)

# 	return(base_image, hsize)

def create_base_image(base_image_location):
	base_image = Image.open(base_image_location)

	wsize_ori = base_image.size[0]
	hsize_ori = base_image.size[1]

	# print(wsize_ori,hsize_ori)

	if wsize_ori < hsize_ori:
		diff_length = (hsize_ori - wsize_ori) / 2
		crop_area = (0, diff_length, wsize_ori, hsize_ori - diff_length)
	elif wsize_ori > hsize_ori:
		diff_length = (wsize_ori - hsize_ori) / 2
		crop_area = (diff_length, 0, wsize_ori - diff_length, hsize_ori)
	else:
		crop_area = (0,0,wsize_ori, hsize_ori)


	# crop_area = (0,10,1080,1070)
	base_image = base_image.crop(crop_area)

	# print(base_image.size[0],base_image.size[1])

	# Resize the image

	basewidth = 1000
	wpercent = (basewidth/float(base_image.size[0]))
	wsize = int((float(base_image.size[0])*float(wpercent)))
	hsize = int((float(base_image.size[1])*float(wpercent)))
	base_image = base_image.resize((basewidth,hsize), Image.ANTIALIAS)
	base_image.save('resized.png')

	# print(wsize,hsize)

	return(base_image, hsize)
	# print(hsize)

# create_base_image2('test2.png')


def create_route_image(lat, lon):
	for activity in range(len(lat)):
	    plt.plot(lon, lat, color = 'deepskyblue', lw = 4, alpha = 0.8)

	filename = 'app/static/temp/route_image_raw.png'
	plt.axis('off')
	plt.savefig(filename, transparent=True, bbox_inches='tight', pad_inches=0, dpi=300)
	

	# RESIZE ROUTE IMAGE

	route_image = Image.open('app/static/temp/route_image_raw.png')

	basewidth = 465
	wpercent = (basewidth/float(route_image.size[0]))
	hsize = int((float(route_image.size[1])*float(wpercent)))
	route_image = route_image.resize((basewidth,hsize), Image.ANTIALIAS)
	plt.close()

	return(route_image)


def create_elevation_image(xaxis, yaxis, y2axis):
	plt.figure(figsize=(9,6))
	plt.plot(xaxis,yaxis,color = 'deepskyblue', lw = 0.1, alpha = 0.8)
	plt.fill_between(xaxis, yaxis, y2axis, color="skyblue", alpha=0.6)
	plt.axis('off')

	filename = 'app/static/temp/elevation_image_raw.png'
	plt.savefig(filename, transparent=True, bbox_inches='tight', pad_inches=0, dpi=300)

	# RESIZE ELEVATION IMAGE

	elevation_image = Image.open('app/static/temp/elevation_image_raw.png')

	basewidth = 1000
	wpercent = (basewidth/float(elevation_image.size[0]))
	hsize = int((float(elevation_image.size[1])*float(wpercent)))
	elevation_image = elevation_image.resize((basewidth,hsize), Image.ANTIALIAS)

	crop_area = (111,0,955,hsize)
	elevation_image = elevation_image.crop(crop_area)

	basewidth = 1000
	wpercent = (basewidth/float(elevation_image.size[0]))
	elevation_image = elevation_image.resize((basewidth,hsize), Image.ANTIALIAS)

	plt.close()

	elevation_image.save('app/static/temp/elevation_image.png')


def create_text_box(base_image, xa1, xb1, ya1, yb1, distance_string, elevation_string, duration_string, max_speed_string, avg_speed_string, max_power_string, avg_power_string):
	draw = ImageDraw.Draw(base_image, 'RGBA')

	draw.polygon([(xa1,ya1), (xb1,ya1), (xb1,yb1), (xa1,yb1)], fill=(55, 55, 55, 150), outline=None)

	title_font = ImageFont.truetype("app/fonts/arial.ttf", 25, encoding="unic")
	metric_font = ImageFont.truetype("app/fonts/arialblack.ttf", 25, encoding="unic")

	spacing1 = 37
	spacing2 = 37

	xtext1 = 640
	xtext2 = 820

	ytextinit1 = 585
	ytextinit2 = 580

	ytext1a, ytext2a, ytext3a, ytext4a, ytext5a, ytext6a, ytext7a = ytextinit1, ytextinit1+(1*spacing1) , ytextinit1+(2*spacing1), ytextinit1+(3*spacing1), ytextinit1+(4*spacing1), ytextinit1+(5*spacing1), ytextinit1+(6*spacing1)
	ytext1b, ytext2b, ytext3b, ytext4b, ytext5b, ytext6b, ytext7b = ytextinit2, ytextinit2+(1*spacing2) , ytextinit2+(2*spacing2), ytextinit2+(3*spacing2), ytextinit2+(4*spacing2), ytextinit2+(5*spacing2), ytextinit2+(6*spacing2)

	# draw.text((680, 500), 'Distance\nElevation\nDuration\nMax Speed\nAvg Speed\nMax Power\nAvg Power', font=title_font, spacing=7, align="left")
	draw.text((xtext1, ytext1a), 'DISTANCE', font=title_font, align="left")
	draw.text((xtext1, ytext2a), 'ELEVATION', font=title_font, align="left")
	draw.text((xtext1, ytext3a), 'DURATION', font=title_font, align="left")
	draw.text((xtext1, ytext4a), 'MAX SPEED', font=title_font, align="left")
	draw.text((xtext1, ytext5a), 'AVG SPEED', font=title_font, align="left")
	draw.text((xtext1, ytext6a), 'MAX POWER', font=title_font, align="left")
	draw.text((xtext1, ytext7a), 'AVG POWER', font=title_font, align="left")

	draw.text((xtext2, ytext1b), distance_string, font=metric_font, align="left")
	draw.text((xtext2, ytext2b), elevation_string, font=metric_font, align="left")
	draw.text((xtext2, ytext3b), duration_string, font=metric_font, align="left")
	draw.text((xtext2, ytext4b), max_speed_string, font=metric_font, align="left")
	draw.text((xtext2, ytext5b), avg_speed_string, font=metric_font, align="left")
	draw.text((xtext2, ytext6b), max_power_string, font=metric_font, align="left")
	draw.text((xtext2, ytext7b), avg_power_string, font=metric_font, align="left")

	base_image.save('app/static/temp/base_image_text.png')


def create_image(activity_id, base_image_input, timenow, code):
	name_string, distance_string, elevation_string, duration_string, max_speed_string, avg_speed_string, max_power_string, avg_power_string, xaxis, yaxis, y2axis, lat, lon = get_data(activity_id,code)
	# activity_info = gact(activity_id)

	# # VARIABLES

	# name = activity_info['name']
	# name_string = str(name)

	# distance = activity_info['distance']
	# distancekm = round(distance/1000,1)
	# distance_string = "{} km".format(str(distancekm))

	# elev_high = activity_info['elev_high']
	# elev_low = activity_info['elev_low']
	# elevation = str(round(elev_high - elev_low,1))
	# elevation_string = "{} m".format(str(elevation))

	# duration = activity_info['moving_time']
	# duration_formatted = time.strftime('%Hh%M', time.gmtime(duration))
	# duration_string = str(duration_formatted)

	# max_speed = round(activity_info['max_speed'],1)
	# max_speed_string = "{} kph".format(str(max_speed))

	# avg_speed = round(activity_info['average_speed'],1)
	# avg_speed_string = "{} kph".format(str(avg_speed))

	# # max_power = str(activity_info[]
	# # avg_power = str(activity_info[]
	# max_power_string = '560 watts'
	# avg_power_string = '231 watts'

	# xaxis = []
	# yaxis = []
	# y2axis = []
	# lat = []
	# lon = []


	# GET THE BASE IMAGE

	base_image, hsize = create_base_image(base_image_input)


	# GET THE DATA

	# data = gas(activity_id)['activities']

	# for i in data:
	# 	xaxis.append(i['distance'])
	# 	yaxis.append(i['altitude'])
	# 	y2axis.append(-700)
	# 	lat.append(i['lat'])
	# 	lon.append(i['lon'])


	# GET THE ROUTE IMAGE

	route_image = create_route_image(lat,lon)


	# GET THE ELEVATION IMAGE

	create_elevation_image(xaxis, yaxis, y2axis)


	# ADD TEXT BOX AND TEXT TO BASE IMAGE

	create_text_box(base_image, xa1, xb1, ya1, yb1, distance_string, elevation_string, duration_string, max_speed_string, avg_speed_string, max_power_string, avg_power_string)


	# ADD ROUTE IMAGE AND ELEVATIONTO BASE IMAGE

	base_image_text = Image.open('app/static/temp/base_image_text.png')
	# route_image = Image.open('route_image.png')
	elevation_image = Image.open('app/static/temp/elevation_image.png')

	base_image_text.paste(route_image, box=(0, 630), mask=route_image)
	base_image_text.paste(elevation_image, box=(0, 800), mask=elevation_image)

	base_image_text.save('app/static/img/image_{}_{}_{}.png'.format(base_image_input,str(activity_id),timenow))
	# base_image_text.save('http://localhost:5000/static/img/base_image_final.png')

	# END ADDING ROUTE AND ELEVATION IMAGE

	return base_image_text



# create_image(activity_id)
# name_string, distance_string, elevation_string, duration_string, max_speed_string, avg_speed_string, max_power_string, avg_power_string, xaxis, yaxis, y2axis, lat, lon = get_data(activity_id)
# create_route_image([1,2,3,4],[56,66,77,2])
# create_elevation_image(xaxis,yaxis,y2axis)
# print(xaxis,yaxis,y2axis)
# data = gact(2271908329)
# pprint(len(data['segment_efforts']))
