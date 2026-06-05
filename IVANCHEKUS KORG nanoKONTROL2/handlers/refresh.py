from ui import *
from midi import *
from mixer import *
import app_state as state


def on_refresh(flags):
	dirty_mix_sel = flags & HW_Dirty_Mixer_Sel
	dirty_mix_disp = flags & HW_Dirty_Mixer_Display
	dirty_mix_ctrl = flags & HW_Dirty_Mixer_Controls
	dirty_leds = flags & HW_Dirty_LEDs
	dirty_rlinks = flags & HW_Dirty_RemoteLinks
	dirty_perf = flags & HW_Dirty_Performance
	dirty_chngrp = flags & HW_Dirty_ChannelRackGroup
	
	mode = state.kn.current_mode

	state.kn.selected_tracks()

	if state.config.SleepTimer:
		if dirty_mix_sel or dirty_mix_disp or dirty_mix_ctrl or dirty_leds:
			state.kn.active[1] = True

	if dirty_mix_sel and state.config.SelectedPeak:
		state.nm.track = trackNumber()

	if dirty_mix_ctrl:	# Triggers on script-restart
		if not state.kn.init_range:
			if mode == 0:
				state.kn.clean_colors()
				if state.config.RangeDisplayRect: state.kn.set_mixer_rectangle()
				elif state.config.ColoredRange: state.kn.set_range_color()
			if mode == 1:
				if state.config.ChannelRectCtrl: state.kn.set_channel_rectangle()

	if mode == 0 and state.nm.statuslights_ready():
		if dirty_mix_sel and dirty_mix_ctrl: state.kn.set_smr_status()	# Update the SMR lights when the mixer changes

	if dirty_leds:
		state.kn.set_transport_status()	# Update Play/Record lights when playing/record starts/stops
		if state.nm.statuslights_ready():
			if mode == 1:
				#state.kn.ch_rect_pos[1] = state.kn.ch_rect_init()[1]
				if state.kn.crdisplayrect > 0:
					state.kn.set_channel_rectangle()
				else: state.kn.set_smr_status()
	elif dirty_chngrp:
		if state.config.ChannelRectCtrl:
			if state.kn.crdisplayrect > 0: state.kn.set_channel_rectangle() #state.kn.set_channel_rectangle(reset=True)
	
	if dirty_mix_disp and state.config.BracketedRange:
		if mode == 0 and state.kn.no_brackets():	# Add brackets when a track inside the range changes name
			state.kn.rename_range(1)

	if dirty_rlinks and dirty_perf:	# Only triggered on start/reload of a project
		if state.config.Debug: print("Script re-initialized")
		if mode == 0:
			state.kn.set_mixer_range(1)
			state.kn.clean_colors()
			if state.config.RangeDisplayRect: state.kn.set_mixer_rectangle()
			elif state.config.ColoredRange: state.kn.set_range_color()
		state.kn.active[1] = True

	if state.config.Debug:
		#	These are kept for debugging purposes
		if flags & HW_Dirty_Mixer_Sel:	print("HW_Dirty_Mixer_Sel")
		if flags & HW_Dirty_Mixer_Display:	print("HW_Dirty_Mixer_Display")
		if flags & HW_Dirty_Mixer_Controls:	print("HW_Dirty_Mixer_Controls")
		if flags & HW_Dirty_RemoteLinks:	print("HW_Dirty_RemoteLinks")
		if flags & HW_Dirty_FocusedWindow:	print("HW_Dirty_FocusedWindow")
		if flags & HW_Dirty_Performance:	print("HW_Dirty_Performance")
		if flags & HW_Dirty_LEDs:	print("HW_Dirty_LEDs")
		if flags & HW_Dirty_RemoteLinkValues:	print("HW_Dirty_RemoteLinkValues")
