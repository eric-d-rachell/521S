# OBD2.py
import obd

class OBD2():
	commands = obd.commands

	def __init__(self):
		try:
			self.OBD_conn = obd.OBD(obd.scan_serial()[0])
			self.connected = True
			print(self.OBD_conn.status())
		except:
			self.connected = False

	def getVIN(self):
		try:
			b_VIN = (self.OBD_conn.query(obd.commands.VIN))
			try:
				VIN = str(b_VIN.value.decode()) # Set Collection to specific VIN, pretty neat right?
			except:
				print('OBD2 dongle is not plugged in.')
				raise
		except:
			VIN = '0123456789AFCDEF'
			print('Default VIN: ' + VIN)
			self.connected = False
		return VIN

	def request(self, cmds):
		res = []
		for cmd in cmds:
			res.append(self.OBD_conn.query(cmd))
		return res

	def test(self):
		try:
			b_VIN = (self.OBD_conn.query(obd.commands.VIN))
			VIN = str(b_VIN.value.decode()) # Set Collection to specific VIN, pretty neat right?
			print('VIN: ' + VIN)
		except:
			print('OBD2 is not connected.')


# Uncomment the follwoing lines for a basic unit test.
#obd2 = OBD2()
#obd2.test()
