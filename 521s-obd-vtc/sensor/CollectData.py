from gps3.agps3threaded import AGPS3mechanism
from time import sleep
from MPUxThread import MPUxThread
import sys
import datetime

DEBUG_MSG = True

agps_thread = AGPS3mechanism()	# Instantiate AGPS3 Mechanisms
agps_thread.stream_data()	# From localhost (), or other hosts,
							# by example, (host='gps.ddns.net')
agps_thread.run_thread()	# Throttle time to sleep after an empty lookup,
							# default '()' 0.2 sec

localTimeDelta = datetime.datetime.now() - datetime.datetime.utcnow()
localTimeDelta += datetime.timedelta(0, 0.45)	# round

timestamp = datetime.datetime.now().isoformat()[:19]
print("Time start: " + timestamp)
timestamp = timestamp.replace(":", "-")
file = open("/home/pi/data/gps_" + timestamp + ".csv", "w")

mpu = MPUxThread(0.003, "/home/pi/data/mpu_" + timestamp + ".csv")
mpu.start()

sleep(3)
for i in range(300):
	mpu.reset()
	sleep(1)

	while agps_thread.data_stream.time=='n/a':	# APGS thread provides the latest fix.
		print('GPS data is not ready.')
		mpu.reset()
		sleep(1)

	time  = agps_thread.data_stream.time
	lat   = agps_thread.data_stream.lat
	lon   = agps_thread.data_stream.lon
	alt   = agps_thread.data_stream.alt
	speed = agps_thread.data_stream.speed
	climb = agps_thread.data_stream.climb
	track = agps_thread.data_stream.track

	if True:
		time = datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ')	# get UTC
		time = time + localTimeDelta	# convert UTC to local
		time = time.isoformat()
		file.write('{}, {}, {}, {}, {}, {}, {}\n'.format(
					time[11:19], lat, lon, alt, speed, climb, track))
	else:
		file.write('{}, {}, {}, {}, {}, {}, {}\n'.format(
					time[11:19], lat, lon, alt, speed, climb, track))

	if DEBUG_MSG:
		print('---------------------')
		print(                    time)
		print('lat.:{}   '.format(lat))
		print('lon.:{}   '.format(lon))
		print('alt.:{}   '.format(alt))
		print('speed:{}  '.format(speed))
		print('climb:{}  '.format(climb))
		print('course:{} '.format(track))

	if DEBUG_MSG:
		Ax, Ay, Az, Gx, Gy, Gz, Tc = mpu.getMean()	# get MPU mean values
		print ("Tc=%.2f" %Tc, u'\u00b0'+ "C", "\tGx=%.3f" %Gx, u'\u00b0'+ "/s", "\tGy=%.3f" %Gy, u'\u00b0'+ "/s", "\tGz=%.3f" %Gz, u'\u00b0'+ "/s", "\tAx=%.4f g" %Ax, "\tAy=%.4f g" %Ay, "\tAz=%.4f g" %Az)

file.close()

mpu.stop()
mpu.join()

timestamp = datetime.datetime.utcnow().isoformat()[:19]
print("Time stop: " + timestamp)

