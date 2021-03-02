import numpy as np
from gps3.agps3threaded import AGPS3mechanism
from time import sleep
import math
import smbus		#import SMBus module of I2C
import threading
from threading import Thread
from datetime import datetime
from AnomalyAnalyzer import AnomalyAnalyzer

UTC       = False
REL_TIME  = False

class MPUxThread(Thread):

	# Some MPU6050 Registers and their Address
	PWR_MGMT_1   = 0x6B
	SMPLRT_DIV   = 0x19
	CONFIG       = 0x1A
	GYRO_CONFIG  = 0x1B
	ACCL_CONFIG  = 0x1C
	INT_ENABLE   = 0x38
	ACCEL_XOUT_H = 0x3B
	ACCEL_YOUT_H = 0x3D
	ACCEL_ZOUT_H = 0x3F
	TEMP_OUT_H   = 0x41
	GYRO_XOUT_H  = 0x43
	GYRO_YOUT_H  = 0x45
	GYRO_ZOUT_H  = 0x47

	file = None

	def __init__(self, data_cycle=0.01, filename=None):
		Thread.__init__(self)

		self.analyzer = AnomalyAnalyzer()

		if filename!=None:
			self.file = open(filename, "w")

		self.running = False
		self._key_lock = threading.Lock()
		self.data_cycle = data_cycle
		self.bus = smbus.SMBus(1)  # or bus = smbus.SMBus(0) for older version boards
		self.Device_Address = 0x68 # MPU6050 device address

		# write to sample rate register
		self.bus.write_byte_data(self.Device_Address, self.SMPLRT_DIV, 7)
		
		# Write to power management register
		self.bus.write_byte_data(self.Device_Address, self.PWR_MGMT_1, 1)
		
		# Write to Configuration register
		self.bus.write_byte_data(self.Device_Address, self.CONFIG, 0)
		
		# Write to Gyro configuration register
		self.bus.write_byte_data(self.Device_Address, self.GYRO_CONFIG, 0)  #± 250°/s
		
		# Write to acceleration configuration register
		self.bus.write_byte_data(self.Device_Address, self.ACCL_CONFIG, 16)  #± 8g
		
		# Write to interrupt enable register
		self.bus.write_byte_data(self.Device_Address, self.INT_ENABLE, 1)

	def read_raw_data(self, addr):
		# Accelero and Gyro value are 16-bit
		high = self.bus.read_byte_data(self.Device_Address, addr)
		low  = self.bus.read_byte_data(self.Device_Address, addr+1)

		# Concatenate higher and lower value
		value = ((high << 8) | low)
		
		# get signed value from mpu6050
		if value > 32768:
				value = value - 65536
		return value

	def reset(self):
		self._key_lock.acquire()
		self.data=[]
		self._key_lock.release()

	# override run() of the Thread class
	def run(self):
		GyroSensitivityAdj = 1
		AcclSensitivityAdj = 4
		self.reset()

		if self.file!=None:
			if REL_TIME:
				if UTC:
					start = datetime.utcnow()
				else:
					start = datetime.now()

		try:
			while self.running:
				# Read Accelerometer raw value
				acc_x = self.read_raw_data(self.ACCEL_XOUT_H)
				acc_y = self.read_raw_data(self.ACCEL_YOUT_H)
				acc_z = self.read_raw_data(self.ACCEL_ZOUT_H)
				
				# Read Gyroscope raw value
				gyro_x = self.read_raw_data(self.GYRO_XOUT_H)
				gyro_y = self.read_raw_data(self.GYRO_YOUT_H)
				gyro_z = self.read_raw_data(self.GYRO_ZOUT_H)

				temp = self.read_raw_data(self.TEMP_OUT_H)

				# Full scale range +/- 250 degree/C as per sensitivity scale factor
				Ax = acc_x / 16384.0 * AcclSensitivityAdj
				Ay = acc_y / 16384.0 * AcclSensitivityAdj
				Az = acc_z / 16384.0 * AcclSensitivityAdj

				Gx = gyro_x / 131.0 * GyroSensitivityAdj
				Gy = gyro_y / 131.0 * GyroSensitivityAdj
				Gz = gyro_z / 131.0 * GyroSensitivityAdj

				Tc = temp / 340.0 + 36.53

				if self.file!=None:
					if UTC:
						now = datetime.utcnow()
					else:
						now = datetime.now()
					if REL_TIME:
						delta = now - start
						time = delta.days*24*3600 + delta.seconds + delta.microseconds/1000000
					else:
						time = now.isoformat()[11:-3]
					self.file.write('{}, {}, {}, {}, {}, {}, {}, {}\n'.format( \
									time, Ax, Ay, Az, Gx, Gy, Gz, Tc))

				self._key_lock.acquire()
				self.data.append ([Ax, Ay, Az, Gx, Gy, Gz, Tc])
				self._key_lock.release()

				sleep(self.data_cycle)

			if self.file!=None:
				self.file.close()

		except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
			self.running = False
			if self.file!=None:
				self.file.close()
			print ("\nKilling Thread...")

	def start(self):
		self.running = True
		Thread.start(self)
		
	def stop(self):
		self.running = False

	def getMean(self):
		if self.getDataLength() == 0:
			raise RuntimeError("No data available: Request data too soon.")

		self._key_lock.acquire()
		data = np.asarray(self.data).mean(axis=0).tolist()
		self._key_lock.release()
		return data

	def getStdDev(self):
		if self.getDataLength() == 0:
			raise RuntimeError("No data available: Request data too soon.")

		self._key_lock.acquire()
		data = np.std(np.asarray(self.data), axis=0).tolist()
		self._key_lock.release()
		return data

	def getAccelMean(self):
		if self.getDataLength() == 0:
			raise RuntimeError("No data available: Request data too soon.")

		self._key_lock.acquire()
		data = np.asarray(self.data).mean(axis=0)[0:3].tolist()
		self._key_lock.release()
		return data

	def getAccelStdDev(self):
		if self.getDataLength() == 0:
			raise RuntimeError("No data available: Request data too soon.")

		self._key_lock.acquire()
		data = np.std(np.asarray(self.data), axis=0)[0:3].tolist()
		self._key_lock.release()
		return data

	def getGyroMean(self):
		if self.getDataLength() == 0:
			raise RuntimeError("No data available: Request data too soon.")

		self._key_lock.acquire()
		data = np.asarray(self.data).mean(axis=0)[3:6].tolist()
		self._key_lock.release()
		return data

	def getGyroStdDev(self):
		if self.getDataLength() == 0:
			raise RuntimeError("No data available: Request data too soon.")

		self._key_lock.acquire()
		data = np.std(np.asarray(self.data), axis=0)[3:6].tolist()
		self._key_lock.release()
		return data

	def getDataLength(self):
		self._key_lock.acquire()
		length = len(self.data)
		self._key_lock.release()
		return length

	def getAnomalies(self):
		if self.getDataLength() == 0:
			raise RuntimeError("No data available: Request data too soon.")

		self._key_lock.acquire()
		data = np.asarray(self.data)[:,0:3]  # We don't need angle rates & temperature.
		self._key_lock.release()

		return self.analyzer.getAnomalies(data)

	def test(self):
		self.start()
		for i in range(10):
			self.reset()
			sleep(1)
			x, y, z = self.getAccelMean()
			print('x={}, y={}, z={}'.format(x,y,z))
			x, y, z = self.getGyroMean()
			print('gx={}, gy={}, gz={}'.format(x,y,z))


# Uncomment the follwoing lines for a basic unit test.
#mpu = MPUxThread()
#mpu.test()
