# VSManager.py
import serial
import pynmea2
import json
import requests
import string
import random
from bson import json_util
from datetime import datetime
from time import sleep
from pymongo import MongoClient

from time import sleep
from MPUxThread import MPUxThread
import sys

from OBD2 import OBD2
from GPS import GPS
from MPUxThread import MPUxThread

DEBUG = False

obd2 = OBD2()
VIN = obd2.getVIN()
print('{}: VIN:{}'.format(datetime.now(), VIN))
route_hash = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

# Setup DB
URI = "mongodb://piOBD:521s@54.186.6.245/obdVTC"
conn = MongoClient(URI)
db = conn["obdVTC"]
collection = db[VIN]	# I am not sure what this is for.


mpu = MPUxThread(0.010)
mpu.start()

gps = GPS()

counter = 0
while True:
	mpu.reset()
	sleep(1)

	# ----- GPS data ----- #
	try:
		while not gps.isReady():
			print(str(datetime.now()) + ': GPS data is not ready.')
			mpu.reset()
			sleep(1)
		longitude = gps.getLongitude()
		latitude  = gps.getLatitude()
		gps_speed = gps.getSpeed()

		#if DEBUG:
		#	print('longitude={}, latitude={}'.format(longitude, latitude))
	except:
		print('{}: Reading GPS failed.'.format(datetime.now()))
		continue


	# ----- MPU data ----- #
	try:
		x, y, z = mpu.getAccelMean()		# get acceleration

		if DEBUG:
			print('x={}, y={}, z={}'.format(x, y, z))
	except:
		print('{}: Reading MPU failed.'.format(datetime.now()))
		continue

	anomalies = mpu.getAnomalies()
	for anomaly in anomalies:
		print(anomaly)

	# ----- BT DONGLE ----- #
	cmds = [OBD2.commands.SPEED, OBD2.commands.RPM, OBD2.commands.THROTTLE_POS]
	try:
		if obd2.connected:
			res = obd2.request(cmds)
			speed = res[0].value.to('mph')
			rpm = res[1].value
			throttle_pos = res[2].value
		else:
			speed = gps_speed
			rpm = 0
			throttle_pos = 0

		if DEBUG:
			print('speed={}, rpm={}, throttle_pos={}'.format(speed, rpm, throttle_pos))
	except:
		print('{}: Reading OBD2 dongle failed.'.format(datetime.now()))
		continue


	# ----- POST DATA ----- #
	data = {
		'hash': route_hash,
		'speed': str(speed),
		'rpm': str(rpm),
		'throttle position': str(throttle_pos),
		'latitude': str(latitude),
		'longitude': str(longitude),
		'anomalies': anomalies,
		'packetNumber': counter,
		'timestamp': datetime.now()
	}

	collection.insert_one(data)		

	postURI = "http://54.186.6.245:5000/pub"
	try:
		pass
		j = json.loads(json_util.dumps(data))
		requests.post(postURI, json=j)
		print(str(datetime.now()) + ": Sent Packet #" + str(counter))
	except:
		print('{}: Posting data failed. URI: {}'.format(datetime.now(), postURI))
		continue

	counter = counter + 1
