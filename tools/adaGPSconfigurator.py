#!/usr/bin/python

from functools import partial

import Tkinter
import bma_serial
import gpshelp
import re
import time

btn_off = "red"
btn_on = "green"

class gpsconfig_tk(Tkinter.Tk):
	def __init__(self,parent):
		Tkinter.Tk.__init__(self,parent)
		self.parent = parent

		self.create_gui_bits()
		#self.read_settings()
		self.comm_established = False

	def create_gui_bits(self):
		self.grid()

		self.bauds = [4800,9600,14400,19200,38400,57600,115200]
		self.baud_lbl = Tkinter.Label(self,text="Baud rate")
		self.baud_lbl.grid(column=0, row=0, sticky='W')
		self.baud_pic = Tkinter.Spinbox(self)
		self.baud_pic["values"] = (4800,9600,14400,19200,38400,57600,115200)
		self.baud_pic.grid(column=1, row=0, columnspan=2)
		self.read_config = Tkinter.Button(self,
		                                  text="Read current settings",
		                                  bg=btn_on)
		self.read_config["command"] = self.read_settings
		self.read_config.grid(column=3, row=0, columnspan=2)
		self.baud_btn = Tkinter.Button(self, text='Set new baud rate')
		self.baud_btn["command"] = self.t_baud
		self.baud_btn.grid(column=5, row=0, columnspan=2)


		self.QUIT = Tkinter.Button(self,text="Quit",fg="red")
		self.QUIT["command"] = self.quit
		self.QUIT.grid(column=7, row=0)

		self.freqs = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]
		self.freq_lbl = Tkinter.Label(self, text="Update rate (Hz)")
		self.freq_lbl.grid(column=0, row=1, sticky='W')
		self.freq_pic = Tkinter.Listbox(self, height=len(self.freqs))
		for x in self.freqs:
			self.freq_pic.insert('end', '%4.1f' % x)
		self.freq_pic.grid(column=1, row=1, columnspan=2)
		self.freq_btn = Tkinter.Button(self, text="Commit chg")
		self.freq_btn["command"] = self.t_freq
		self.freq_btn.grid(column=3, row=1, columnspan=2)

		self.labelNMEArow = Tkinter.Label(self, text="NMEA sentences")
		self.labelNMEArow.grid(column=0, row=2, sticky='W')
		self.nmeasentences = []
		for i,s in enumerate(['GLL', 'RMC', 'VTG', 'GGA', 'GSA', 'GSV']):
			self.nmeasentences.append(Tkinter.Button(self, text=s,
			                                         bg=btn_off))
			#self.nmeasentences[i]["command"] = lambda: self.t_sentence(i)
			self.nmeasentences[i]["command"] = partial(self.t_sentence, i)
			self.nmeasentences[i].grid(column=i+1, row=2)

		self.sbas_lbl = Tkinter.Label(self, text="SBAS")
		self.sbas_lbl.grid(column=0, row=3, sticky='W')

		self.sbas_btn = Tkinter.Button(self, text="In use", bg=btn_off)
		self.sbas_btn["command"] = lambda: self.toggle(self.sbas_btn,
		                                               'PMTK313')
		self.sbas_btn.grid(column=1, row=3)

		self.sbasint_btn = Tkinter.Button(self, text="Integrity",
		                                  bg=btn_off)
		self.sbasint_btn["command"] = lambda: self.toggle(self.sbasint_btn,
		                                                  'PMTK319')
		self.sbasint_btn.grid(column=2, row=3)

		self.waas_btn = Tkinter.Button(self, text="WAAS", bg=btn_off)
		self.waas_btn["command"] = lambda: self.toggle(self.waas_btn,
		                                               'PMTK301', '2')
		self.waas_btn.grid(column=3, row=3)

		self.ver_lbl = Tkinter.Label(self, text="Firmware version")
		self.ver_lbl.grid(column=0, row=4, sticky='W')
		self.ver_txt = Tkinter.Label(self)
		self.ver_txt.grid(column=1, row=4, columnspan=4, sticky='W')

		self.navspds = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0]
		self.navspd_lbl = Tkinter.Label(self,
		                                text="Nav speed threshold (m/s)")
		self.navspd_lbl.grid(column=0, row=5, sticky='W')
		self.navspd_pic = Tkinter.Listbox(self, height=len(self.navspds))
		for x in self.navspds:
			self.navspd_pic.insert('end', '%3.1f' % x)
		self.navspd_pic.grid(column=1, row=5, columnspan=2)
		self.navspd_btn = Tkinter.Button(self, text="Commit chg")
		self.navspd_btn["command"] = self.t_navspd
		self.navspd_btn.grid(column=3, row=5, columnspan=2)

	def t_baud(self):
		if not self.comm_established:
			print "t_baud: Aborting, serial comm not active"
			return False
		
		newbaud = self.baud_pic.get()
		print('t_baud: Setting new baudrate to %s' % newbaud)
		pmtk_phrase = 'PMTK251,%s' % newbaud

		cksum = reduce(lambda x,y: x ^ ord(y), list(pmtk_phrase), 0)
		self.ser.write('$%s*%X\r\n' % (pmtk_phrase, cksum))
		self.ser.flush()
		time.sleep(4)
		if self.init_comm():
			self.read_config["bg"] = 'yellow'
			self.baud_btn["bg"] = btn_on
			return True
		else:
			self.read_config["bg"] = btn_off
			self.baud_btn["bg"] = btn_off
			return False

	def t_sentence(self, sentence):
		if not self.comm_established:
			print "SenToggle: Aborting, serial comm not active"
			return False

		pmtk_phrase = 'PMTK314'
		print('SenToggle: Called to toggle element [%d]' % sentence)
		if self.nmeasentences[sentence]["bg"] == btn_on:
			new_state = btn_off
			pmtk_fragment = '0'
		else:
			new_state = btn_on
			pmtk_fragment = '1'

		for i in range(len(self.nmeasentences)):
			if i == sentence:
				pmtk_phrase += ',%s' % pmtk_fragment
			else:
				current_state = self.nmeasentences[i]["bg"] 
				pmtk_phrase += ',1' if current_state == btn_on else ',0'

		pmtk_phrase += ',0,0,0,0,0,0,0,0,0,0,0,0,0'
		print('SenToggle: Switching NMEA using [%s]' % pmtk_phrase)
		if self.pmtk_cmd(pmtk_phrase):
			self.nmeasentences[sentence]["bg"] = new_state
			return True
		else:
			return False
			

	def t_freq(self):
		if not self.comm_established:
			print "t_freq: Aborting, serial comm not active"
			return False

		new_freq_hz = self.freqs[self.freq_pic.curselection()[0]]
		pmtk_phrase = 'PMTK220,%d' % (1000 / new_freq_hz)
		print('tfreq: %s' % pmtk_phrase)
		if self.pmtk_cmd(pmtk_phrase):
			current = self.measure_freq()
			for x,y in enumerate(self.freqs):
				bgcolor = btn_on if y==current else btn_off
				self.freq_pic.itemconfig(x, background=bgcolor)
			self.freq_btn["bg"] = btn_on
			return True
		else:
			self.freq_btn["bg"] = btn_off
			return False

	def toggle(self, widget, pmtk_phrase, onval=1, offval=0):
		if not self.comm_established:
			print "Toggle: Aborting, serial comm not active"
			return False

		if widget["bg"] == btn_on:
			new_state = btn_off 
			pmtk_phrase += ',%s' % offval
		else:
			new_state = btn_on 
			pmtk_phrase += ',%s' % onval

		print('Toggle: Switch %s with [%s]' % (widget["text"],pmtk_phrase))
		if self.pmtk_cmd(pmtk_phrase):
			widget["bg"] = new_state
			return True
		else:
			return False

	def t_navspd(self):
		if not self.comm_established:
			print "t_navspd: Aborting, serial comm not active"
			return False

		new_navspd = self.navspds[self.navspd_pic.curselection()[0]]
		pmtk_phrase = 'PMTK386,%3.1f' % new_navspd
		print('t_navspd: Sending new navspeed %3.1f' % new_navspd)
		if self.pmtk_cmd(pmtk_phrase):
			current = self.pmtk_pkt('PMTK447', 'PMTK527').split(',')[1]
			for x,y in enumerate(self.navspds):
				bgcolor = btn_on if y==float(current) else btn_off
				self.navspd_pic.itemconfig(x, background=bgcolor)
			self.navspd_btn["bg"] = btn_on
			return True
		else:
			self.navspd_btn["bg"] = btn_off

	def init_comm(self):
		self.ser = bma_serial.BMA_Serial(port='/dev/ttyUSB0',
		                                 baudrate=int(self.baud_pic.get()),
		                                 timeout=1)
		print('Testing comm with timeout %3.1f...' % self.ser.timeout)
		self.ser.write('$PMTK605*31\r\n')
		for x in range(4):
			z = self.ser.readuntil('\n', self.ser.timeout)
			if z and re.search('PMTK705,AXN_2.31_3339', z):
				current = self.pmtk_pkt('PMTK605', 'PMTK705').split(',')[1]
				self.ver_txt["text"] = current
				self.comm_established = True
				return True
			else:
				print('  !!! Timeout / garbage. Retrying...')

		print('!!! Giving up. Try a different baud rate or settings.')
		self.comm_established = False
		return False

	def pmtk_pkt(self, send, rcv):
		cksum = reduce(lambda x,y: x ^ ord(y), list(send), 0)
		print('>>> $%s*%X' % (send, cksum))
		self.ser.write('$%s*%X\r\n' % (send, cksum))
		line = ''
		while not re.search(rcv, line):
			line = self.ser.readline()
		print('               %s <<<' % (line.rstrip()))
		return line.split('*', 1)[0]

	def pmtk_cmd(self, send):
		print('pmtk_cmd: Sending command')
		current = self.pmtk_pkt(send, 'PMTK001')
		if current.split(',')[2] == '3':
			print('                 --> success')
			return True
		else:
			print('                 --!!! failed')
			return False
			
	def measure_freq(self):
		nmea_type = ''
		base = 0
		span = 0
		print("--> Measuring sentence output rate")

		for x in range(5):
			c = self.ser.readuntil('\n', 11)

			if not nmea_type and re.search('GP(GGA|RMC)', c):
				nmea_type = c.split(',')[0]
				print('   Using %s sentences for reference' % nmea_type)
			elif c.split(',')[0] != nmea_type:
				continue

			#'$GPGGA,123519.200,blah,bleh,ork' -> '19.200'
			if not base:
				base = float(c.split(',')[1][4:])
			else:
				z = float(c.split(',')[1][4:])
				if z < base:
					z += 60
				print('  >>> Found the differential: %4.1f' % (z-base))
				return 1 / float('%4.1f' % (z-base))

		return False

	def read_settings(self):
		self.read_config["bg"] = 'yellow'

		if not self.init_comm():
			self.read_config["bg"] = btn_off
			return False

		current = self.measure_freq()
		for x,y in enumerate(self.freqs):
			bgcolor = btn_on if y==current else btn_off
			self.freq_pic.itemconfig(x, background=bgcolor)
			
		current = self.pmtk_pkt('PMTK414', 'PMTK514')
		state = current.split(',')[1:7]
		for i,s in enumerate(state):
			self.nmeasentences[i]["bg"] = btn_on if int(s) else btn_off
		
		current = self.pmtk_pkt('PMTK413', 'PMTK513').split(',')[1]
		self.sbas_btn["bg"] = btn_on if int(current) else btn_off

		current = self.pmtk_pkt('PMTK419', 'PMTK519').split(',')[1]
		self.sbasint_btn["bg"] = btn_on if int(current) else btn_off

		current = self.pmtk_pkt('PMTK401', 'PMTK501').split(',')[1]
		self.waas_btn["bg"] = btn_on if current == '2' else btn_off

		current = self.pmtk_pkt('PMTK447', 'PMTK527').split(',')[1]
		for x,y in enumerate(self.navspds):
			bgcolor = btn_on if y==float(current) else btn_off
			self.navspd_pic.itemconfig(x, background=bgcolor)
		
		self.read_config["bg"] = btn_on
		return True

if __name__ == "__main__":
	print "\n !!!! NOTE !!!!\nIf \"Read current settings\" keeps failing but you're pretty sure you've got the right baud rate, just keep retrying. The probe answers are sometimes lost in the normal flood of NMEA sentences.\n"
	app = gpsconfig_tk(None)
	app.title("GPS Configurator")
	app.mainloop()
