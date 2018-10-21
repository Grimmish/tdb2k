import serial
import datetime

class BMA_Serial(serial.Serial):
	def readuntil(self, stopchar, timeout=1):
		collect = ''
		stime = datetime.datetime.now()

		while True:
			byte = self.read(1)
			try:
				if byte and byte.decode('ascii'):
					if byte.decode("ascii") == stopchar:
						return collect
					else:
						collect += byte.decode("ascii")
			except Exception:
				pass

			timer = datetime.datetime.now() - stime
			if timer.total_seconds() > timeout:
				return False
