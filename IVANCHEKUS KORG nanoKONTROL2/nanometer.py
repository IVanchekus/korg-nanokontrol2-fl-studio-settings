from time import time

from device import midiOutMsg
from mixer import getTrackPeaks, getTrackVolume
from transport import isPlaying
from midi import MIDI_CONTROLCHANGE

import app_state as state
from midi_map import SMR_LIGHT_ROWS


class NanoMeter:

	def __init__(self):
		self.lights = SMR_LIGHT_ROWS
		self.track = 0
		self.lastrow = 0
		self.maxedpeak = -50
		self.last_L, self.last_R = 0, 0
		self.volume = 0
		self.silence = 0
		self.lastmode = False
		self.clip_L, self.clip_R = None, None
		self.cliplight = [False,False]
		self.peak_list = self.create_peak_list(0)
		self.cc = MIDI_CONTROLCHANGE
		self.midichan = state.config.MIDIChannel - 1
		self.play = False
		self.clear = False


	def main(self):
		db = lambda x: -59.027+382.756*x+-2690.004*x**2+12192.951*x**3+-33120.365*x**4+54482.221*x**5+-53090.953*x**6+28161.016*x**7+-6258.646*x**8
		config = state.config
		kn = state.kn
		maxedpeak = self.maxedpeak
		last_L = self.last_L
		last_R = self.last_R
		L,R = None, None
		volume = getTrackVolume(0)
		wasplaying = self.play
		silenttime = self.silence
		lastmode = self.lastmode
		t = time()

		if config.BigMeter: peaks = (2,2)
		else: peaks = (0,1)

		peak_L = getTrackPeaks(self.track,peaks[0])
		peak_R = getTrackPeaks(self.track,peaks[1])
		peak_LR = db(getTrackPeaks(self.track,2))
		light_L = self.get_rows_from_peak(db(peak_L))
		light_R = self.get_rows_from_peak(db(peak_R))

		if peak_LR > maxedpeak:
			self.peak_list = self.create_peak_list(peak_LR)
			self.maxedpeak = peak_LR
		elif maxedpeak - peak_LR > 7.5:
			if self.maxedpeak > -49: self.maxedpeak -= 0.3

		if self.volume != volume:
			self.maxedpeak = -50

		if peak_L + peak_R < 0.001 and silenttime == 0 and maxedpeak > -50:
			silenttime = time()
		elif silenttime > 0 and t - silenttime > 0.1:
			self.maxedpeak = -50
			silenttime = 0
			self.clear = False
			if not config.PlayingOnly:
				if config.Debug: print("Peaklight  reset")
				kn.set_smr_status()

		if peak_L + peak_R > 0.032 and peak_L == peak_R:
			if config.BigMeter: L = None
			else: L = 'M'
			R = None
		elif peak_L + peak_R > 0.032:
			L = 'S'
			R = 'R'

		if not config.PlayingOnly or config.PlayingOnly and isPlaying():
			if L and L != lastmode:
				if config.Debug: print("Stereo/Mono mode changed")
				self.set_light(8,1,0)
				last_L = 0
				last_R = 0

		if self.statuslights_ready():
			if wasplaying and not isPlaying():
				self.set_light(8,1,0)
				kn.set_smr_status()
				if config.Debug: print("Peaklight  reset")
		else:
			if config.Clipping:
				if self.clipping(peak_L,0):
					if last_L == 8: last_L -= 1
				elif self.cliplight[0]:
					if L: self.set_light(8,8,0,'S')
					else: self.set_light(8,8,0)
					self.cliplight[0] = False
				if self.clipping(peak_R,1):
					if last_R == 8: last_R -= 1
				elif self.cliplight[1]:
					if R: self.set_light(8,8,0,'R')
					else: self.set_light(8,8,0)
					self.cliplight[1] = False

			if not config.PlayingOnly:
				if peak_L + peak_R > 0.01:
					if  not self.clear:
						self.set_light(1,8,0)
						self.clear = True
			elif not wasplaying and isPlaying():
						self.set_light(1,8,0)
						last_L = 0
						last_R = 0

			if light_L > last_L:
				self.set_light(last_L,light_L,1,L)
			elif light_L < last_L:
				self.set_light(last_L,light_L,0,L)

			if R:
				if light_R > last_R:
					self.set_light(last_R,light_R,1,R)
				elif light_R < last_R:
					self.set_light(last_R,light_R,0,R)

		self.last_L= light_L
		self.last_R= light_R
		self.volume = volume
		if L: self.lastmode = L
		self.play = isPlaying()
		self.silence = silenttime


	def get_rows_from_peak(self,db_peak,peak_list=None):
		if not peak_list: peak_list = self.peak_list

		abs_diff = lambda list_value : abs(list_value - db_peak)
		closest_value = min(peak_list, key=abs_diff)
		return peak_list.index(closest_value)


	def create_peak_list(self,db_peak):
		span = [2.5, 2.5, 2.5, 5.0, 5.0, 7.5, 7.5, 15.5]
		if db_peak < -45: db_peak = -45
		x = (-48 - db_peak) / -48
		newspan = [x * i for i in span]
		dblist = []
		for i in span:
			dblist.append(db_peak - sum(newspan))
			newspan.pop()
		dblist.append(db_peak)
		return dblist


	def clipping(self,peak,mode):
		if type(peak) is not float: raise TypeError("peak argument must be of type 'float'")
		if type(mode) is not int: raise TypeError("mode argument must be of type 'int'")
		if mode not in range(0,2): raise ValueError("mode argument must be '1' or '2'")

		t = time()
		clip = [self.clip_L, self.clip_R]
		last = [self.last_L, self.last_R]

		if peak > 1:
			clip[mode] = [t]
			self.cliplight[mode] = True
		elif peak < 1 and clip[mode] and len(clip[mode]) < 3:
			if t - clip[mode][-1] >= 1: clip[mode].append(t)
			if last[mode] > 7: last[mode] = 7
		elif peak < 1 and clip[mode] and len(clip[mode]) > 2:
			clip[mode] = None

		if mode == 0:
			self.clip_L = clip[0]
			self.last_L = last[0]
		elif mode == 1:
			self.clip_R = clip[1]
			self.last_R = last[1]

		if clip[mode]: return True
		else: return False


	def set_light(self,start_row, end_row, state_val, light = None):
		start_row = start_row or 1
		config = state.config
		if config.ReversePeak: lights = self.lights[::-1]
		else: lights = self.lights
		chan = self.midichan
		cc = self.cc
		smr = 'SMR'

		if light and len(light) == 1:
			if light in smr: button = smr.index(light)
			else: light = None

		if state_val: vel=127
		else: vel=0

		if end_row == 0:
			end_row = 1
			vel=0

		if end_row < start_row:
			start_row, end_row = end_row, start_row
			rows = range(start_row-1,end_row)[::-1]
		else: rows = range(start_row-1,end_row)

		for row in rows:
			if not light:
				for btn in lights[row]:
					midiOutMsg(cc,chan,btn,vel)
			else: midiOutMsg(cc,chan,lights[row][button],vel)


	def statuslights_ready(self):
		config = state.config
		if not config.PeakMeter: return True
		if config.PlayingOnly and not isPlaying(): return True
		elif not config.PlayingOnly:
			if getTrackPeaks(self.track,2) < 0.001: return True
		return False
