from time import time
from ui import *
from midi import *
from channels import *
from device import *
from mixer import *
from arrangement import *
from transport import *
import app_state as state


def on_control_change(event):
	event.handled = True 					# Set the event as handled for now so it does not get sent to FL Studio unless we want it to
	button = event.data1
	faders = state.kn.faders
	knobs = state.kn.knobs
	smr_btns = state.kn.smr_btns
	track_select = state.kn.track_select
	markers = state.kn.markers
	transp_btns = state.kn.transp_btns
	solo = state.kn.smr('S')
	mute = state.kn.smr('M')
	rec = state.kn.smr('R')
	mode = state.kn.current_mode

	if state.config.Debug: print("Id:",event.midiId, "Ch:",event.midiChan,"d1:",event.data1, "d2:", event.data2)		# Prints the recieved MIDI data to the 'Script output' window

	if event.data2 > 0:
	
		if button in smr_btns:	# Handle S,M,R buttons
			if state.nm.statuslights_ready():
				try:
					if state.kn.control_not_linked(event.data1):
						if mode == 0 and not state.kn.shift:
							if state.config.RangeRectTimer: state.kn.hl_timecheck = time()
							track = state.kn.smr_tracks[button]
							if button in solo: soloTrack(track)
							elif button in mute: muteTrack(track)
							elif button in rec:
								if state.config.ArmedTracks: armTrack(track)
								elif state.config.MultiSelect: selectTrack(track) 
								else: setTrackNumber(track)
						elif mode == 1 and not state.kn.shift:
							if state.config.ChannelRectCtrl:
								if button in state.kn.smr_chtracks:
									track = state.kn.smr_chtracks[button]
									if button in solo: soloChannel(track)
									elif button in mute: muteChannel(track)
							else:
								nr = selectedChannel()
								if button == 19: soloChannel(nr)
								elif button == 20: muteChannel(nr)
				except (TypeError, RuntimeError):
				# state.kn.control_not_linked() throws an exception when creating controller links.
				# This will catch the error silently.
					event.handled = False

				if state.config.LinkOverriding:
					event.handled = False
				else:
					if mode == 3 or state.kn.shift:
						if state.kn.shift: state.kn.shiftevent = True
						event.handled = False	# Pass the event to FL Studio
						state.kn.smr_press(event)
						if state.kn.set_held: state.kn.link_control(button)

		elif button in faders:	# Handle mixer faders
			try:
				if state.kn.control_not_linked(event.data1):
					if mode == 0 and not state.kn.shift:
						if len(state.kn.selectedtracks) > 1: state.kn.multi_fader (event.data1,event.data2)
						else: state.kn.volume_fader(event.data1,event.data2)
					elif mode == 1 and not state.kn.shift: state.kn.channel_control(event)
					elif mode == 2 and not state.kn.shift: state.kn.playlist_zoom(event)
			except (TypeError, RuntimeError):
				event.handled = False

			if state.config.LinkOverriding:
				event.handled = False
			else:
				if mode == 3 or state.kn.shift:
					if state.kn.shift: state.kn.shiftevent = True
					event.handled = False
					if state.kn.set_held:
						if not state.kn.link_created: state.kn.link_control(button)


		elif button in knobs:	# Handle mixer knobs
			try:
				if state.kn.control_not_linked(event.data1):
					if mode == 0 and not state.kn.shift: state.kn.mixer_knobs(event.data1,event.data2)
					elif mode == 0 and state.kn.shift: state.kn.mixer_knobs(event.data1,event.data2,False)
					elif mode == 1 and not state.kn.shift: state.kn.channel_control(event)
					elif mode == 2 and not state.kn.shift: state.kn.tempo_knob(event)
			except (TypeError, RuntimeError):
				event.handled = False

			if state.config.LinkOverriding:
				event.handled = False
			else:
				if mode == 3 or state.kn.shift:
					if state.kn.shift: state.kn.shiftevent = True
					event.handled = False
					if state.kn.set_held:
						if not state.kn.link_created: state.kn.link_control(button)

		elif button in track_select:	# Handle track-select buttons
			if not state.kn.shift:
				if mode == 0:
					if state.kn.set_held:
						state.kn.vol_ftune(button)
						state.kn.set_repeat_event(button,0.4,0.15,state.kn.vol_ftune)
					else:
						state.kn.sel_mixer(button)
						state.kn.set_repeat_event(button,0.4,0.18,state.kn.sel_mixer)
				elif mode == 1:
					state.kn.toggle_channel_rect(button)
				elif mode == 2:
					state.kn.playlist_nav(button)
					state.kn.set_repeat_event(button,0.4,0.1,state.kn.playlist_nav)
			
		elif button in markers:	# Handle set and marker buttons
			if state.kn.shift:
				if mode == 0: state.kn.split_master(button)
				if mode == 2: state.kn.handle_markers(button)
			else:
				if mode == 0:
					if button == 3:
						state.kn.preserve_mixdiff(event)
						state.kn.set_held = True
					else:
						state.kn.move_range(button)
						state.kn.set_repeat_event(button,0.4,0.2,state.kn.move_range)
				elif mode == 1:
					if state.config.ChannelRectCtrl:
						state.kn.ch_rect_navigation(button)
						state.kn.set_repeat_event(button,0.4,0.13,state.kn.ch_rect_navigation)
					else:
						state.kn.set_channel(button)
						state.kn.set_repeat_event(button,0.4,0.11,state.kn.set_channel)
				elif mode == 2:
					state.kn.playlist_nav(button)
					state.kn.set_repeat_event(button,0.4,0.1,state.kn.playlist_nav)
				elif mode == 3:
					if button == 3:
						state.kn.set_held = True
					else:
						state.kn.set_channel(button)
						state.kn.set_repeat_event(button,0.4,0.15,state.kn.set_channel)

		elif button in transp_btns:
			if state.kn.shift: state.kn.quick_save(event)
			else: state.kn.set_transport(event)

		elif button == 2:	# Cycle button
			state.kn.set_mode(event)

	elif event.data2 == 0:	# Handle button-release events

		state.kn.active[1] = True
	
		if button in track_select + markers:	# Track-select release
			if mode == 0:
				if button == 3:
					state.kn.set_held = False
					state.kn.preserve_mixdiff(event)
					if not state.kn.ftune: state.kn.move_range(button)
					state.kn.ftune = False
			if mode == 3:
				if button == 3:
					state.kn.set_held = False
					state.kn.link_created = False
			if not state.kn.shift:
				if button in state.kn.repeat_events.keys(): del state.kn.repeat_events[button]
			
		elif button in transp_btns:	# Transport button release
			if state.kn.shift: state.kn.quick_save(event)
			else: state.kn.set_transport(event)

		elif button == 2:	# Cycle button
			if state.kn.mode_blinks > 0: state.kn.mode_blink(True)
			state.kn.set_mode(event)

		elif mode == 3 or state.kn.shift:
			event.handled = False	# Pass the event to FL Studio
			state.kn.smr_press(event)
