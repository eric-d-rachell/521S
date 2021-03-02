# GPS.py
from gps3.agps3threaded import AGPS3mechanism
from time import sleep

DEBUG = True

class GPS:
	def __init__(self):
		self.agps_thread = AGPS3mechanism()	# Instantiate AGPS3 Mechanisms
		self.agps_thread.stream_data()	# From localhost (), or other hosts,
										# by example, (host='gps.ddns.net')
		self.agps_thread.run_thread()	# Throttle time to sleep after an empty lookup,
										# default '()' 0.2 sec

	def isReady(self):
		return self.agps_thread.data_stream.time!='n/a'

	def getLongitude(self):
		 return self.agps_thread.data_stream.lon

	def getLatitude(self):
		return self.agps_thread.data_stream.lat

	def getAltitude(self):
		return self.agps_thread.data_stream.alt

	def getSpeed(self):
		return self.agps_thread.data_stream.speed

	def getLocation(self):
		return [self.agps_thread.data_stream.lon, \
				self.agps_thread.data_stream.lat, \
				self.agps_thread.data_stream.alt]


	def test(self):
		while True:
			sleep(1)
			#while not gps.isReady():
			#	print('GPS data is not ready.')
			#	sleep(1)
			longitude = gps.getLongitude()
			latitude  = gps.getLatitude()
			altitude  = gps.getAltitude()
			print('longitude={}, latitude={}'.format(longitude, latitude, altitude))


# Uncomment the follwoing lines for a basic unit test.
#gps = GPS()
#gps.test()
