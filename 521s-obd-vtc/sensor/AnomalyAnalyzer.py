import numpy as np

class AnomalyAnalyzer():

	def __init__(self):
		# self.AcclXMean =  0.0396
		# self.AcclXStd  =  0.1060
		# self.AcclYMean = -0.0073
		# self.AcclYStd  =  0.0989
		# self.AcclZMean =  1.0065
		# self.AcclZStd  =  0.0798

		# self.GyroXMean = -1.2640
		# self.GyroXStd  =  2.3900
		# self.GyroYMean = -1.4143
		# self.GyroYStd  =  4.6457
		# self.GyroZMean = -1.3217
		# self.GyroZStd  =  7.0733

		self.AcclXLimit = 0.5
		self.AcclYLimit = 0.5
		self.AcclZLimit = 2.0

	def getAnomalies(self, data):
		list = []

		# noise filter
		scoop = 3
		data0 = np.asarray(data)
		data1 = data[scoop:].copy()
		for i in range(scoop):
			data1 += data0[i:i-scoop]
		data = data1 / (scoop+1)

		length = len(data)
		minX, minY, minZ = np.min(data, axis=0)
		maxX, maxY, maxZ = np.max(data, axis=0)

		# Test if more than 2 elements greater than limit

		# Test Y acceleration
		impact = False
		if np.sum(data[:,1] > self.AcclYLimit) > 1:
			impact = True
			argmaxY = np.argmax(data[:,1])
		else:
			argmaxY = len(data)-1
		if np.sum(data[:,1] < -self.AcclYLimit) > 1:
			impact = True
			argminY = np.argmin(data[:,1])
		else:
			argminY = len(data)-1
		if impact:
			if argmaxY < argminY:
				list.append("Front Impact")
			else:
				list.append("Rear Impact")

		# Test X acceleration
		impact = False
		if np.sum(data[:,0] > self.AcclXLimit) > 1:
			impact = True
			argmaxX = np.argmax(data[:,0])
		else:
			argmaxX = len(data)-1
		if np.sum(data[:,0] < -self.AcclXLimit) > 1:
			impact = True
			argminX = np.argmin(data[:,0])
		else:
			argminX = len(data)-1
		if impact:
			if argmaxX < argminX:
				list.append("Right Impact")
			else:
				list.append("Left Impact")

		return list
