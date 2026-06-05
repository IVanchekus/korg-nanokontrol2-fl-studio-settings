from time import time
from ui import *
from midi import *
from channels import *
from device import *
from mixer import *
from arrangement import *
from transport import *
from general import *
import app_state as state
from midi_map import TRACK_SELECT, MARKERS, TRANSPORT, KNOBS, FADERS, SMR_BUTTONS, smr_cc_indices
import volume as volume_util
from volume import VOLUME_TABLE, END_TABLE
import fader_pickup as fp


class Kontrol:

	def __init__(self):
	#	Initiates a lot of stuff
		self.tracks = []
		self.smr_tracks = {}
		self.smr_chtracks = {}
		self.mixer_range = []
		self.ftune_volume = [None for i in range(8)]
		self.fader_pickup = [False] * 8
		self.pickup_blink_phase = False
		self.pickup_blink_last = 0
		self.set_mixer_range(1)
		self.ch_rect_start = 0
		self.repeat_events = {}		
		self.defaultcolors = {}
		self.init_range = False
		self.modes = self.get_modes(0)
		self.current_mode = self.get_modes(1)
		self.lastzoom_x, self.lastzoom_y = 0, 0
		self.lastfocus = 2
		self.lastknob = 0
		self.faderknob = [0,1]
		self.hl_timecheck = 0
		self.midisplayrect = False
		self.lighttoggle = 0
		self.savelighttoggle = 0
		self.shift = False
		self.shiftevent = False
		self.set_held = False
		self.ftune = False
		self.active = [time(),True,0]
		self.flash_transp = 0
		self.flash_transp_data = [0,0]
		self.mode_blinks = 0
		self.loopmode = None
		self.metronome = None
		self.volume = None
		self.faderlock = [0,time()]
		self.selectedtracks = {}
		self.mixdiff = state.config.PreserveMixDiff
		self.track_select = TRACK_SELECT
		self.markers = MARKERS
		self.transp_btns = TRANSPORT
		self.knobs = KNOBS
		self.smr_btns = list(SMR_BUTTONS)
		self.faders = FADERS
		self.volume_table = VOLUME_TABLE
		self.end_table = END_TABLE
		self.pickup = True if getVersion() >= 13 else False
		self.link_created = False
		self.set_channel_rectangle(hide=True) if state.config.ChannelRectCtrl else self.set_channel_rectangle(clear=True)
		print(
			" _ __   __ _ _ __   ___  _ __ ___   ___| |_ ___ _ __\n"
			"| '_ \\ / _` | '_ \\ / _ \\| '_ ` _ \\ / _ \\ __/ _ \\ '__|\n"
			"| | | | (_| | | | | (_) | | | | | |  __/ ||  __/ |\n"
			"|_| |_|\\__,_|_| |_|\\___/|_| |_| |_|\\___|\\__\\___|_|\n"
			"by Robin Calvin (olyrhc)\n"
			"forked by IVanchekus | https://github.com/IVanchekus"
		)


	def smr(self,key):
		return smr_cc_indices(key)


	def has_pickup_active(self):
		return state.config.FaderPickup and any(self.fader_pickup)


	def _button_in_pickup_slot(self, button):
		if not state.config.FaderPickup:
			return False
		for pos in range(min(8, len(self.fader_pickup))):
			if not self.fader_pickup[pos]:
				continue
			if button in (self.smr('S')[pos], self.smr('M')[pos], self.smr('R')[pos]):
				return True
		return False


	def update_fader_pickup(self):
		if not state.config.FaderPickup:
			self.fader_pickup = [False] * 8
			return
		for i in range(len(self.mixer_range)):
			cc = fp.slot_cc_value(self.ftune_volume, i)
			track = self.mixer_range[i]
			if cc is None:
				self.fader_pickup[i] = True
			else:
				self.fader_pickup[i] = not fp.volumes_match(cc, getTrackVolume(track))


	def pickup_blink_handler(self):
		if not self.has_pickup_active():
			return
		t = time()
		if t - self.pickup_blink_last < 0.3:
			return
		self.pickup_blink_last = t
		self.pickup_blink_phase = not self.pickup_blink_phase
		cc = MIDI_CONTROLCHANGE
		chan = state.config.MIDIChannel - 1
		vel = 127 if self.pickup_blink_phase else 0
		for pos in range(min(8, len(self.fader_pickup))):
			if not self.fader_pickup[pos]:
				continue
			midiOutMsg(cc, chan, self.smr('S')[pos], vel)
			midiOutMsg(cc, chan, self.smr('M')[pos], vel)
			midiOutMsg(cc, chan, self.smr('R')[pos], vel)


	def set_smr_status(self):
	#	This is used to update the lights of the Solo, Mute and Record buttons
		buttons = self.smr_btns
		cc = MIDI_CONTROLCHANGE
		chan = state.config.MIDIChannel - 1
		mode = self.current_mode
		nr = selectedChannel()
		solo = 127 if isChannelSolo(nr) else 0
		mute = 127 if isChannelMuted(nr) else 0
		channels = channelCount()
		start = self.ch_rect_start
		end = start + 8 if channels >= 8 else channels

		for button in buttons:
			if self._button_in_pickup_slot(button):
				continue
			midiOutMsg(cc,chan,button,0)

		if mode == 0:	# Activate the buttons light if the corresponding mixer state is set
			for pos, track in enumerate(self.mixer_range):
				if state.config.FaderPickup and pos < len(self.fader_pickup) and self.fader_pickup[pos]:
					continue
				solo = 127 if isTrackSolo(track) else 0
				mute = 127 if isTrackMuted(track) else 0
				if state.config.ArmedTracks: rec = 127 if isTrackArmed(track) else 0
				else: rec = 127 if isTrackSelected(track) else 0
				midiOutMsg(cc,chan,self.smr('S')[pos],solo)
				midiOutMsg(cc,chan,self.smr('M')[pos],mute)
				midiOutMsg(cc,chan,self.smr('R')[pos],rec)
		
		elif mode == 1:	# Activate the buttons light if the corresponding channel rack state is set
			if state.config.ChannelRectCtrl:
				for pos, channel in enumerate(range(self.ch_rect_start,end)):
					solo = 127 if isChannelSolo(channel) else 0
					mute = 127 if isChannelMuted(channel) else 0
					midiOutMsg(cc,chan,self.smr('S')[pos],solo)
					midiOutMsg(cc,chan,self.smr('M')[pos],mute)
			else:
				midiOutMsg(cc,chan,19,solo)
				midiOutMsg(cc,chan,20,mute)


	def volume_fader(self,fader,val):
	#	This takes the input from the nanoKontrol faders and use it to set the volume

		n = self.faders.index(fader)
		track = self.mixer_range[n]

		if state.config.FaderPickup and self.fader_pickup[n]:
			self.ftune_volume[n] = val
			if not fp.volumes_match(val, getTrackVolume(track)):
				return
			self.fader_pickup[n] = False
			self.set_smr_status()

		if self.set_held:
			if self.ftune_volume[n]:
				if val < self.ftune_volume[n]:
					self.vol_ftune(0,track)
				elif val > self.ftune_volume[n]:
					self.vol_ftune(1,track)
		else:
			self.vol_ctrl(setTrackVolume,track,val)

		if track > 0: self.faderknob[0] = time()
		if state.config.RangeRectTimer > 0: self.hl_timecheck = time()
		self.ftune_volume[n] = val


	def multi_fader(self,fader,val):
	#	This takes the input from one slider and adjusts the volume on all the selected tracks
		n = self.faders.index(fader)
		if state.config.FaderPickup and self.fader_pickup[n]:
			self.ftune_volume[n] = val
			if not fp.volumes_match(val, getTrackVolume(self.mixer_range[n])):
				return
			self.fader_pickup[n] = False
			self.set_smr_status()
		lockedfader = self.faderlock_handler(fader)
		volume = val / 127 - 0.003
		db = self.to_db
		fl = self.to_fl

		if fader == lockedfader:
			tracks = self.selectedtracks.items()
			selected = sorted(tracks, key=lambda item: item[1], reverse=self.mixdiff)
			firsttrack = selected[0][0]
			firstvol = selected[0][1]
			absolutevol = getTrackVolume(firsttrack)

			for track,trackvol in selected:
				dbdiff = round(db(firstvol),2) - round(db(trackvol),3)
				if self.volume:
					voldiff = self.volume - volume
					newvolume = round(absolutevol - voldiff,3)
					diffvolume = fl(db(newvolume) - dbdiff)
					if trackvol == firstvol:
						diffvolume = newvolume
					setTrackVolume(track,diffvolume)
			self.volume = volume


	def to_db(self,volume_val):
		return volume_util.to_db(volume_val, self.volume_table, self.end_table)


	def to_fl(self,db):
		return volume_util.to_fl(db, self.volume_table, self.end_table)


	def faderlock_handler(self,fader):
	#	Gives the currently used slider exclusive control of the selected tracks while it's being used
		faderlock = self.faderlock
		if time() - faderlock[1] > 0.3:
			self.faderlock = [fader,time()]
			self.volume = None
		elif fader == faderlock[0]:
			self.faderlock[1] = time()
		return self.faderlock[0]


	def selected_tracks(self,update=False):
	#	Returns a dict of all the selected tracks in the mixer
		insert_tracks = trackCount() - 1
		tracklist = ()
		selectedtracks = {}
		for track in range(insert_tracks):
			if isTrackSelected(track):
				tracklist += (track,)
		for track in tracklist:
			selectedtracks[track] = getTrackVolume(track)
		if len(selectedtracks) != len(self.selectedtracks) or update:
			self.selectedtracks = selectedtracks


	def preserve_mixdiff(self,event):
	#	Enables/disables "PreserveMixDiff" for the SET button depending on the config option
		if len(self.selectedtracks) > 1 and event.data1 == self.markers[0]:
			if not state.config.PreserveMixDiff:
				if event.data2 == 127: self.mixdiff = True
				else: self.mixdiff = False
			else:
				if event.data2 == 127: self.mixdiff = False
				else: self.mixdiff = True


	def vol_ftune(self,button,slider=False):
	#	This controls the fine-tuning of the selected mixer track/tracks
		selected = self.selectedtracks

		def apply_vol(track):
			trackvol = getTrackVolume(track)
			if trackvol <= 0.00102: trackvol = 0.00265
			vol = [key for key in self.volume_table.keys() if key >= trackvol][-1]
			dist = self.volume_table[vol][1]

			if button == self.track_select[0]:
				newvol = trackvol - dist * 1
				if trackvol < 0.002715: return 0.002715
				else: return newvol
			elif button == self.track_select[1]:
				newvol = trackvol + dist * 1
				return newvol

		if len(selected) > 1:
			for track in selected:
				newvol = apply_vol(track)
				setTrackVolume(track,newvol)
			self.selected_tracks(True)
			self.ftune = True
		elif not slider and len(selected) == 1:
			track = trackNumber()
			newvol = apply_vol(track)
			setTrackVolume(track,newvol)
			self.ftune = True
		elif slider:
			newvol = apply_vol(slider)
			setTrackVolume(slider,newvol)
			self.ftune = True


	def vol_ctrl(self,setFunc,target,value):
	#	Wrapper method with extra logic for volume control
		volume = value / 127 - 0.003
		if volume < 0.01: volume = 0
		elif volume > 0.99: volume = 1
		if self.pickup: setFunc(target,volume,2)
		else: setFunc(target,volume)


	def knob_ctrl(self,setFunc,target,value,no_pickup=False):
	#	Wrapper method with extra logic for pan control
		pan = value / 127 * 2 - 1.008
		if pan < -0.99: pan = -1
		elif pan > 0.99: pan = 1
		if self.pickup and not no_pickup:
			setFunc(target, pan, 2)
		else: setFunc(target, pan)


	def mixer_knobs(self,knob,val,pan=True):
	#	This takes the input from the nanoKontrol knobs and use it to set the panning or stereo separation
		if not pan:
			setFunc = setTrackStereoSep
			self.shiftevent = True
		else: setFunc = setTrackPan

		knoblist = self.knobs
		mixer_range = self.mixer_range
		n = knoblist.index(knob)
		track = mixer_range[n]
		self.knob_ctrl(setFunc,track,val)
		if track > 0: self.faderknob[0] = time()
		if state.config.RangeRectTimer > 0: self.hl_timecheck = time()


	def channel_control(self,event):
	#	Handles the control of the channel rack
		knobs = self.knobs
		faders = self.faders
		ctrl = event.data1
		val = event.data2
		channel = selectedChannel()

		if self.crdisplayrect == 1:	# Checks if channelrack rectangle is active
			if ctrl in knobs:	#	Sets the channel pan
				chan = self.ch_rect_start + knobs.index(ctrl)
				if chan < channelCount():
					self.knob_ctrl(setChannelPan,chan,val)
			if ctrl in faders:	#	Sets the channel volume
				chan = self.ch_rect_start + faders.index(ctrl)
				if chan < channelCount():
					self.vol_ctrl(setChannelVolume,chan,val)
		else:
			if ctrl == knobs[0]:	#	Sets the channel pan
				self.knob_ctrl(setChannelPan,channel,val)
			elif ctrl == knobs[1]:	#	Sets the channel volume
				self.vol_ctrl(setChannelVolume,channel,val)
			elif ctrl == knobs[2]:	#	Changes the target mixer track for the current channel
				current = getTargetFxTrack(channel)
				track = val - 1
				if track > 125: track = 125
				if abs(track - current) == 1:
					setTrackNumber(track,1)
					name = getTrackName(track)
					linkTrackToChannel(0)		# linkTrackToChannel() messes up the track name... :(
					setTrackName(track,name)	# ...so let's change it back again.
			elif ctrl == knobs[3]:  #   Sets the channel pitch
				self.knob_ctrl(setChannelPitch,channel,val,True)


	def set_transport(self,event):
	#	Handles the control of the transport buttons
		transp_btns = self.transp_btns
		cc = MIDI_CONTROLCHANGE
		chan = event.midiChan
		button = event.data1
		vel = event.data2

		def call_transport():
			if button == transp_btns[0]:		# Rewind
				if vel == 127: rewind(2,15)
				elif vel == 0: rewind(0,15)
			elif button == transp_btns[1]:		# FForward
				if vel == 127: fastForward(2,15)
				elif vel == 0: fastForward(0,15)
			elif button == transp_btns[2]:		# Stop
				if vel == 127:
					stop()
					self.loopmode = time()	# Register the time of the keypress for the loopmode event
				elif vel == 0: self.loopmode = None	# Clear the loopmode event
				self.lighttoggle = 0		# Reset lighttoggle

			elif button == transp_btns[3]:		# Play
				if vel == 127:
					start()
					self.metronome = time()
				elif vel == 0: self.metronome = None
			elif button == transp_btns[4] and vel == 127: record()	# Record

		if state.config.TranspBtnLink and (state.config.LinkOverriding or self.current_mode == 3):
			event.handled = False	# Pass the event to FL Studio
			if self.set_held: self.link_control(button)
			else: midiOutMsg(cc,chan,button,vel)
		else:
			call_transport()
			if button in transp_btns[:3]: # Ignore Play and Record lights (handled elsewhere)
				midiOutMsg(cc,chan,button,vel)


	def set_transport_status(self):
	#	Detects if Play or Record is activated and toggles their lights
		light = self.transp_btns
		cc = MIDI_CONTROLCHANGE
		chan = state.config.TransportChan -1

		if isPlaying(): midiOutMsg(cc,chan,light[3],127)
		else: midiOutMsg(cc,chan,light[3],0)

		if isRecording(): midiOutMsg(cc,chan,light[4],127)
		else: midiOutMsg(cc,chan,light[4],0)


	def blink_transp_light(self,toggle_attr,button=-1,flashes=0):
	#	This is used to toggle (flash) the light of the various transport-buttons
		light = self.transp_btns
		cc = MIDI_CONTROLCHANGE
		chan = state.config.TransportChan -1
		playblink = state.config.PlayBlinkTempo

		state = getattr(self,toggle_attr) ^ 1
		setattr(self,toggle_attr,state)

		if flashes:
			self.flash_transp_data = [button, flashes*4]
			setattr(self,toggle_attr,0)
			self.flash_transp = 1

		def blink(n):
			if state: midiOutMsg(cc,chan,light[n],127)
			else: midiOutMsg(cc,chan,light[n],0)

		if self.flash_transp == 0:
			if playblink and isPlaying(): blink(3)
			elif isPlaying() and isRecording(): blink(4)
		else: blink(self.flash_transp_data[0])


	def mode_blink(self,reset=False):
	#	Flashes the transport buttons to indicate the currently active mode
		light = self.transp_btns
		cc = MIDI_CONTROLCHANGE
		chan = state.config.TransportChan -1
		modes = self.get_modes(0)
		current = self.current_mode

		if len(modes) > 1:
			lights = modes.index(current) + 1
		else: return

		if reset:
			for l in range(lights):
				midiOutMsg(cc,chan,light[l],0)
			return

		for l in range(lights):
			if self.mode_blinks % 2:	# Check if mode_blinks is even
				midiOutMsg(cc,chan,light[l],127)
			else:
				midiOutMsg(cc,chan,light[l],0)
		if self.mode_blinks == 14: self.mode_blinks = 0
		else: self.mode_blinks += 1


	def set_mixer_range(self,start):
	#	This generate lists of which tracks are currently controlled
		mixdict = {}
		range_size = 7 if state.config.StickyMaster else 8
		max_start = trackCount() - range_size - 1

		if start < 0 or start > max_start: raise ValueError("start argument must be a number between 0-"+str(max_start))
		if not state.config.StickyMaster:
			mixer = [i for i in range(start,start+8)]	# Generate a list of 8 mixer tracks
			smr_mixer = [i for i in range(start,start+8) for n in range(3)]	# duplicate each track 3 times ('S'+'M'+'R')
					
		else:
			mixer = [0] + [i for i in range(start,start+7)]	# Same as above but start with master track and add 7 tracks
			smr_mixer = [0,0,0] + [i for i in range(start,start+7) for n in range(3)]
		for button, track in enumerate(smr_mixer,19):	#	Use enumerate() to replicate the button numbers
			mixdict[button] = track	# Create a dictionary with buttons as keys and mixer-tracks as values
		self.mixer_range = mixer
		self.smr_tracks = mixdict
		self.update_fader_pickup()


	def sel_mixer(self,button):
	#	This takes input from the track-buttons and use it to select tracks
		mixer_range = self.mixer_range
		master = state.config.StickyMaster
		move = None
		if button == 0: move = -1
		elif button == 1: move = 1
		if not move: return
		selected = trackNumber()

		if state.config.TrackRangeOnly:
			if master and move == 1 and selected == mixer_range[0]:	# from master to first
				setTrackNumber(mixer_range[1],1)
			elif master and move == -1 and selected == mixer_range[1]:	# from first to master
				setTrackNumber(mixer_range[0])

			elif move == 1 and selected == mixer_range[-1]:	# From last to first
				setTrackNumber(mixer_range[0],1)
			elif move == -1 and selected == mixer_range[0]:	# from first to last
				setTrackNumber(mixer_range[-1],1)

			elif selected not in mixer_range:	# if outside range, go to first
				setTrackNumber(mixer_range[0],1)
			elif move == 1: setTrackNumber(selected +1,1)	# move to next
			elif move == -1: setTrackNumber(selected -1,1)	#move to previous
		else:
			if move == 1:
				if selected == 126: setTrackNumber(0)
				else: setTrackNumber(selected +1,1)	# move to next
			elif move == -1:
				if selected == 0: setTrackNumber(126)
				else: setTrackNumber(selected -1,1)	#move to previous


	def set_mixer_rectangle(self,clear=None):
	#	This is used to set the red rectangle that marks the controlled mixer tracks
		self.init_range = True
		if state.config.StickyMaster: start = self.mixer_range[1]
		else: start = self.mixer_range[0]
		end = self.mixer_range[-1]

		if not clear:
			miDisplayRect(start,end,MaxInt,2)
			self.midisplayrect = True
			if state.config.RangeRectTimer > 0: self.hl_timecheck = time()
		else:
			miDisplayRect(start,end,0)
			self.midisplayrect = False


	def set_channel_rectangle(self,**kwargs):
	#	This is used to set the red rectangle that marks the controlled channels.
		channels = channelCount()
		start = self.ch_rect_start
		solo = self.smr('S')
		mute = self.smr('M')
		self.smr_chtracks = {}	# Clear smr_chtracks

		if channels < 8:
			self.ch_rect_start, start = 0, 0
			end = channels
		elif start + 8 > channels:
			start = channels - 8
			end = channels - start
			self.ch_rect_start = start
		else: end = 8

		for i in range(end):	# Create smr_chtracks dict with solo+mute as keys and channels as values
			self.smr_chtracks[solo[i]] = start + i
			self.smr_chtracks[mute[i]] = start + i

		if 'clear' in kwargs: self.crdisplayrect = -1
		if 'hide' in kwargs: self.crdisplayrect = 0
		if 'clear' in kwargs or 'hide' in kwargs:
			crDisplayRect(0,start,0,end,0,10)
		else:
			crDisplayRect(0,start,0,end,MaxInt,10)
			self.crdisplayrect = 1
		if state.config.PeakMeter and isPlaying(): pass
		else: self.set_smr_status()


	def set_range_color(self,state=None):
	#	This is used to change or update the color of the tracks that are controlled
		mixer_range = self.mixer_range
		marked = state.config.HighlightColor
		umarked = -10261391
		found_marked = False
		mark_count = 0
		if state.config.StickyMaster: clear_idx = 1
		else: clear_idx = 0

		def  defaultColor(track):
			if track in self.defaultcolors: color = self.defaultcolors[track]
			else: color = umarked
			return color

		if not state:
			self.defaultcolors = {}
			for track in mixer_range:
				color = getTrackColor(track)
				if color != umarked and color != marked: self.defaultcolors[track] = color
			if state.config.StickyMaster: r1 = mixer_range[1]
			else: r1 = mixer_range[0]
			try: setTrackNumber(r1,1)
			except (TypeError, RuntimeError): pass
			
			for track in mixer_range:
				color = getTrackColor(track)
				if color != marked:
					try: setTrackColor(track,marked)
					except (TypeError, RuntimeError): pass
			
			for track in mixer_range:
				color = getTrackColor(track)
				if color == marked: mark_count +=1
			if mark_count == 8: self.init_range = True	# Flag that coloring is done
			else:
				self.init_range = False
				if state.config.Debug: print("marked tracks found:",mark_count)

		elif state ==1:	# Reset all mixer colors
			for track in mixer_range:
				color = defaultColor(track)
				setTrackColor(track,color)

		elif state > 1:
			if state == 2:	# Update colors for decreasing range
				clear_track = mixer_range[-1] +1
				mark_track = mixer_range[clear_idx]
			if state == 3:	# Update colors for inreasing range
				clear_track = mixer_range[clear_idx] -1
				mark_track = mixer_range[-1]
			if self._valid_track(clear_track):
				setTrackColor(clear_track,defaultColor(clear_track))
			if self._valid_track(mark_track):
				color = getTrackColor(mark_track)
				if color != umarked and color != marked: self.defaultcolors[mark_track] = color
				setTrackColor(mark_track,marked)


	def _valid_track(self, track):
		return track >= 0 and track < trackCount()


	def clean_colors(self):
	#	Resets the default colors (where necessary) for all the mixer-tracks
		marked = state.config.HighlightColor
		rect_master_color = -4177326
		default = -10261391
		
		color = getTrackColor(0)
		if color == rect_master_color: setTrackColor(0,default)

		for track in range(1, trackCount()):
			try:
				color = getTrackColor(track)
				if color == marked: setTrackColor(track,default)
			except (TypeError, RuntimeError): pass


	def rename_range(self,state):
	#	This is used to add brackets to the names of the mixer tracks that are currently controlled
		mixer_range = self.mixer_range
		master = state.config.StickyMaster
		
		if state.config.BracketedRange:
			for track in mixer_range:
				n = getTrackName(track)
				name = None
				if state == 1:	# Rename whole range
					if n[0] != "[" and n[-1] != "]": name = "[" + n + "]"
				elif not state:	# Clear whole range
					if n[0] == "[" and n[-1] == "]": name = n[1:-1]
				try:
					if name: setTrackName(track,name)
				except (TypeError, RuntimeError): pass		# Avoid a script-crash in case FL Studio is busy and throws an error

			if state ==2:		# clear rightmost track
				track = mixer_range[-1] +1
			elif state == 3:	# clear leftmost track
				if master: idx = 1
				else: idx = 0
				track = mixer_range[idx] -1
			try:
				if state > 1:
					n = getTrackName(track)
					if n[0] == "[" and n[-1] == "]": name = n[1:-1]
					if name: setTrackName(track,name)
			except (TypeError, RuntimeError): pass


	def no_brackets(self):
	#	This checks if the current track-name has brackets or not
		track = trackNumber()
		if track in self.mixer_range:
			name = getTrackName(track)
			if name[0] != "[" and name[-1] != "]": return True
			else: return False
		return False


	def move_range(self,button):
	# Handle movement of the controlled mixer tracks
		mixer_range = self.mixer_range
		markers = self.markers
		master = state.config.StickyMaster
		highlight = state.config.ColoredRange
		d_rect = state.config.RangeDisplayRect
		brackets = state.config.BracketedRange
		range_size = 7 if master else 8
		max_start = trackCount() - range_size - 1
		min_start = 1 if master else 0

		if master: track = mixer_range[1]
		else: track = mixer_range[0]

		def check_track_bounds(track):
			if track < min_start or track > max_start:
				return False
			return True

		if button == markers[0] and len(self.selectedtracks) == 1:	# Set-button
			track = trackNumber()
			if check_track_bounds(track):
				if highlight: self.set_range_color(1)
				if brackets: self.rename_range(0)
				self.set_mixer_range(track)
				setTrackNumber(self.mixer_range[-1],1)
				setTrackNumber(track,1)
				if highlight: self.set_range_color()
				if d_rect: self.set_mixer_rectangle()

		elif button == markers[1]:	# Marker prev-button
			track -= 1
			if check_track_bounds(track):
				self.set_mixer_range(track)
				if highlight: self.set_range_color(2)
				if d_rect: self.set_mixer_rectangle()
				if brackets:
					self.rename_range(2)
				if master: idx = 1
				else: idx = 0
				setTrackNumber(mixer_range[-1] -1,1)
				setTrackNumber(mixer_range[idx] -1,1)
					
		elif button == markers[2]:	# Marker next-button
			track += 1
			if check_track_bounds(track):
				self.set_mixer_range(track)
				if highlight: self.set_range_color(3)
				if d_rect: self.set_mixer_rectangle()
				if brackets:
					self.rename_range(3)	# clear brackets to the left of the range
					self.rename_range(1)	# update brackets to include the new track
				setTrackNumber(mixer_range[-1] +1,1)
				setTrackNumber(track,1)


	def split_master(self,button):
	#	This locks/unlocks the master track to the first control group
		self.shiftevent = True
		umarked = -10261391
		mixer_range = self.mixer_range
		markers = self.markers
		highlight = state.config.ColoredRange
		marked = state.config.HighlightColor if highlight else False
		d_rect = state.config.RangeDisplayRect
		brackets = state.config.BracketedRange
		master = state.config.StickyMaster
		skip = False

		if master and self.mixer_range[-1] == trackCount() - 2:
			return	# Abort if the current mixer_range is about to expand past the max track count!

		if self.shift and button == markers[0]:
			if master:
				um, m = 0,  -1
				setTrackNumber(mixer_range[1],1)
			else:
				um, m = -1, 0
				setTrackNumber(mixer_range[0],1)
				if self.mixer_range[0] == 0: skip = True

			if not skip:
				if brackets:
					name = False
					n = getTrackName(mixer_range[um])
					if n[0] == "[" and n[-1] == "]": name = n[1:-1]
					if name: setTrackName(mixer_range[um],name)
				if marked: setTrackColor(mixer_range[um],umarked)

			if master == True: state.config.StickyMaster = False
			elif master == False: state.config.StickyMaster = True
			if skip: setTrackNumber(1,1)
			self.set_mixer_range(trackNumber())
			if marked:
				if d_rect: self.set_mixer_rectangle()
			if brackets:
				name = False
				n = getTrackName(self.mixer_range[m])
				if n[0] != "[" and n[-1] != "]": name = "[" + n + "]"
				if name: setTrackName(self.mixer_range[m],name)


	def set_mode(self,event):
	#	This switches between the Mixer, Channel rack and Playlist modes
		cc = MIDI_CONTROLCHANGE
		chan = event.midiChan
		highlight = None
		brackets = state.config.BracketedRange
		button = event.data1
		vel = event.data2
		windows = ('Mixer','Channel rack','Playlist/Pianoroll','Controller Link mode')
		mode = self.current_mode
		modes = self.modes
		peaks = getTrackPeaks(state.nm.track,2)
		disp = self.crdisplayrect

		if state.config.RangeDisplayRect: highlight = self.set_mixer_rectangle
		elif state.config.ColoredRange: highlight = self.set_range_color

		if len(self.modes) == 0: return	# Break if all modes are disabled in the configfile

		if vel == 127: self.shift = True	# Register as a shift-button when pressed down
		else: self.shift = False

		if vel == 0 and not self.shiftevent:
			i = modes.index(mode)
			if i + 1 < len(modes): mode = modes[i + 1]
			else: mode = modes[0]
			
			if mode == 0:
				if brackets: self.rename_range(1)	# Add brackets to names
				if highlight: highlight()	# Set range colors
				self.update_fader_pickup()
			elif mode > 0 and 0 in modes:
				if highlight: highlight(1)	# Clear range colors
				if brackets: self.rename_range(0)
			if mode == 1:
				if disp == 0: self.set_channel_rectangle()
			elif mode != 1 and 1 in modes:
				if disp == 1: self.set_channel_rectangle(hide=True)

			if mode <=2: showWindow(mode)
			elif mode == 3: showWindow(1)
			setHintMsg(windows[mode])
			self.current_mode = mode
			if peaks < 0.01: self.set_smr_status()

			self.mode_blinks = 1
				
		self.shiftevent = False
		midiOutMsg(cc,chan,button,vel)


	def set_channel(self,button):
	#	Navigates between channels using the marker buttons
		markers = self.markers
		channel = selectedChannel()

		if button == markers[0]:	# marker set
			try:
				showCSForm(channel,-1)
			except (TypeError, RuntimeError):
				showEditor(channel)

		if button ==  markers[1]:	# marker prev
			globalTransport(102,-1,2,15)
			chan = selectedChannel()
			if getVersion() >= 13: scrollWindow(1,chan)
			
		elif button == markers[2]:	# marker next
			globalTransport(102,1,2,15)
			chan = selectedChannel()
			if getVersion() >= 13: scrollWindow(1,chan)
			
		name = getChannelName(channel)
		setHintMsg(name)


	def ch_rect_navigation(self,direction):
	#	Moves the channel rectangle
		disp = self.crdisplayrect
		track_select = self.track_select
		markers = self.markers
		start = self.ch_rect_start
		end = channelCount() - 8

		if direction == markers[0]: # Set button
			if selectedChannel() < end: self.ch_rect_start = selectedChannel()
			else: self.ch_rect_start = end
		elif direction == markers[1]:
			if start > 0:
				self.ch_rect_start -= 1
		elif direction == markers[2]:
				if start < end:
					self.ch_rect_start += 1
		self.set_channel_rectangle()


	def toggle_channel_rect(self,button):
	#	Toggles the channel rectangle on/off
		if button == self.track_select[0]:
			state.config.ChannelRectCtrl = not state.config.ChannelRectCtrl
			if state.config.ChannelRectCtrl: self.set_channel_rectangle()
			else: self.set_channel_rectangle(clear=True)


	def playlist_nav(self,direction):
	#	Navigates the playlist/pianoroll
		track_select = self.track_select
		markers = self.markers
		playlist = getFocused(2)
		pianoroll = getFocused(3)

		if playlist or pianoroll:
			if direction == track_select[0]:
				globalTransport(100,-1,2,15)
			elif direction == track_select[1]:
				globalTransport(100,1,2,15)
			if direction == markers[0]:
				visible = getVisible(3)
				focused = getFocused(3)
				if visible and not focused: setFocused(3)
				elif not visible: showWindow(3)
				else: hideWindow(3)
			elif direction == markers[1]:
				jump = jumpToMarker(-1,0)
				if jump == -1: jog(-1)	# If no markers, jump to next bar instead
			elif direction == markers[2]:
				jump = jumpToMarker(1,0)
				if jump == -1: jog(1)
			if playlist: self.lastfocus = 2
			else: self.lastfocus = 3


	def playlist_zoom(self,event):
	#	Handles the horizontal/vertical zooming of the playlist
		vel = event.data2
		faders = self.faders
		lzx = self.lastzoom_x
		lzy = self.lastzoom_y

		if not getFocused(2) and not getFocused(3):
			return	# Don't do anything if playlist or pianoroll is not focused!

		if event.data1 == faders[0]:		# First fader
			if vel >= lzx + 3:	# Zoom in, fader-throw resolution set to 3 (slow)
				jog(0)
				horZoom(1)
				self.lastzoom_x = vel
			elif vel <= lzx:
				if vel < 20: res = 2	# If throw is small , zoom-out needs to be slightly quicker, resolution set to 2
				else: res = 3
				if vel <= lzx - res:
					jog(0)
					horZoom(-1)
					self.lastzoom_x = vel

		elif event.data1 == faders[1]:	# Second fader
			if vel > lzy:
				verZoom(1)
				self.lastzoom_y = vel
			elif vel < lzy:
				verZoom(-1)
				self.lastzoom_y = vel


	def tempo_knob(self,event):
	#	Changes the current tempo
		knob = event.data1
		knobval = event.data2
		lastknob = self.lastknob
		newtempo = 0
		tempo = int(getCurrentTempo(1))
		base = state.config.TempoBase - 2
		catch = 2

		if knob == self.knobs[0]:
			t = knobval - lastknob
			pos = base + knobval - tempo
			if t < 0 and pos < -1: catch = 4
			elif t > 0 and pos > 1: catch = 4
			if abs(base + knobval - tempo) < catch:
				if t > 0 and tempo <= base+126: newtempo = 10
				elif t < 0 and tempo >= base: newtempo = -10
		
		if newtempo:
			if tempo == state.config.TempoBase and newtempo < 0: pass
			else: globalTransport(105,newtempo,2,15) 
		self.lastknob = knobval


	def repeat_handler(self):
	# 	Handles the repeat-event when a button is held down
		current_time = time()
		repeat_events = self.repeat_events

		for button in repeat_events:
			repeat_event = repeat_events[button]
			press_time = repeat_event[0]
			last_repeat = repeat_event[1]
			delay_time = repeat_event[2]
			repeat_time = repeat_event[3]
			function = repeat_event[4]
			if current_time - press_time > delay_time:
				if current_time - last_repeat > repeat_time:
					function(button)
					repeat_event[1] = time()
					self.repeat_events[button] = repeat_event

	
	def set_repeat_event(self,button,delay_time,repeat_time,function):
	# 	Registers that a button needs to be repeated
		if button != self.markers[0]:
			self.repeat_events[button] = [time(),0,delay_time,repeat_time,function]


	def faderknob_focus(self):
	#	Uses setTrackNumber() to scroll the mixer to the tracks of the controlled range	
		if state.config.StickyMaster: t = 1
		else: t = 0
		selected = trackNumber()
		if getVersion() >= 13:
			scrollWindow(0,self.mixer_range[t])
			scrollWindow(0,self.mixer_range[7])
		else:
			setTrackNumber(self.mixer_range[t],1)
			setTrackNumber(self.mixer_range[7],1)
			setTrackNumber(selected)


	def handle_markers(self,button):
	#	Creates and jumps between markers in the playlist
		markers = self.markers
		self.shiftevent = True
		name = "Marker #"
		names = []
		taken = True
		nr = 1
		x=0

		while True:	# Create a list with all the used marker names
			m = getMarkerName(x)
			if not m: break
			names.append(m)
			x += 1

		while name + str(nr) in names: nr +=1	# Check for the next available name

		if button == markers[0]:
			ct = currentTime(0)
			addAutoTimeMarker(ct,name + str(nr))
		elif button == markers[1]:
			jumpToMarker(-1,0)
		elif button == markers[2]:
			jumpToMarker(+1,0)


	def quick_save(self,event):
	#	Saves the project without highlighted mixer-colors!
		self.shiftevent = True
		mixermode = False
		button = event.data1
		if self.current_mode == 0 and state.config.RangeDisplayRect == False: mixermode = True
		cc = MIDI_CONTROLCHANGE
		chan = event.midiChan
		button = event.data1
		vel = event.data2
		
		def execute_qsave():
			if mixermode: self.set_range_color(1)
			globalTransport(92,1,6,15)
			self.blink_transp_light('savelighttoggle',4,3)
			if mixermode: self.set_range_color()

		if state.config.TranspBtnLink:
			if button == self.transp_btns[4] and self.control_not_linked(button):
				execute_qsave()
			else:
				midiOutMsg(MIDI_CONTROLCHANGE,event.midiChan,button,vel)
				event.handled = False
		elif button == self.transp_btns[4]: execute_qsave()




	def pause(self,pause=None):
	#	Triggers random SMR-lights as a pause-effect
		cc = MIDI_CONTROLCHANGE
		smr_chan = state.config.MIDIChannel - 1
		lights = self.smr_btns[:]
		
		def reset():
			for l in lights: midiOutMsg(cc,smr_chan,l,0)
		
		def rand_val(x):
			random=int(time()*1000)
			random %= x
			return random
		
		def pause_mode():
			p_lights = lights[:]
			reset()
			for l in range(12):
				nr = rand_val(len(p_lights))
				midiOutMsg(cc,smr_chan,p_lights[nr],127)
				p_lights.pop(nr)
		
		if pause == 1:
			if state.config.Debug:
				if time() - self.active[0] < (state.config.SleepTimer * 60) + 2: print("Pause mode active")
			pause_mode()
			self.active[2] = time()
			return
		elif pause == 2:
			if state.config.Debug: print("Pause mode deactivated")
			reset()
			return


	def get_modes(self,current):
	#	Returns an array with the modes that are enabled in the config.
	#	It's also used to set the default mode at startup.
		modes = []
		if state.config.MixerMode: modes.append(0)
		if state.config.ChannelrackMode: modes.append(1)
		if state.config.PlaylistMode: modes.append(2)
		if state.config.ControllerLinkMode and not state.config.LinkOverriding: modes.append(3)
		if current:
			if len(modes) > 0: return modes[0]
			else: return None
		return modes


	def smr_press(self,event):
	#	Turns the pressed Solo/Mute/Rec buttons light on or off.
		if event.data2 == 127: midiOutMsg(event.midiId,event.midiChan,event.data1,127)
		elif event.data2 == 0: midiOutMsg(event.midiId,event.midiChan,event.data1,0)


	def control_not_linked(self,cc):
	# Checks to see if the cc is currently linked in FL Studio
		midichan = state.config.TransportChan if cc in self.transp_btns else state.config.MIDIChannel

		try:	# EncodeRemoteControlID lacks proper documentation in the API. Let's put a try/except just in case.
			id = findEventID(EncodeRemoteControlID(getPortNumber(), midichan-1, 0) + cc, 1)
			val = getLinkedValue(id)
			if val == -1: return True
			else: return False
		except (TypeError, RuntimeError):
			return False	# Assume control is linked if findEventID fails


	def link_control(self,button):
	#	This is used to link a button/knob/slider to the last tweaked parameter
		midichan = state.config.TransportChan if button in self.transp_btns else state.config.MIDIChannel

		if getVersion() >= 21:
			link = linkToLastTweaked(button,midichan,True)
			if link == 0:
				self.blink_transp_light('savelighttoggle',4,3)
				self.link_created = True
		else: print('Error: linkToLastTweaked requires a newer version of FL Studio!')


