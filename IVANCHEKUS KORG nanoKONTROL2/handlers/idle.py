from time import time
from mixer import *
from transport import *
import app_state as state


def on_idle():
	if not state.script_ready():
		return
	mode = state.kn.current_mode
	flashtransp = state.kn.flash_transp
	flash_end = state.kn.flash_transp_data[1]
	modeblinks = state.kn.mode_blinks
	faderknob = state.kn.faderknob

	if state.kn.repeat_events:
		state.kn.repeat_handler()

	if state.kn.loopmode:
		if time() - state.kn.loopmode > 0.7:
			setLoopMode()
			state.kn.loopmode = None

	if state.kn.metronome:
		if time() - state.kn.metronome > 0.7:
			globalTransport(110,1,2,15)
			state.kn.metronome = None

	if flashtransp and flashtransp <= flash_end:
		if flashtransp % 2:	# Check if flash_transp is even
			state.kn.blink_transp_light('savelighttoggle')
		state.kn.flash_transp += 1
		if flashtransp == flash_end: state.kn.flash_transp = 0

	if state.config.ModeBlink:
		if modeblinks > 0: state.kn.mode_blink()

	if faderknob[1] and time() - faderknob[0] < 3:
		state.kn.faderknob_focus()	# Focus the mixertrack if a fader/knob was moved
		state.kn.faderknob[1] = False
	elif time() - faderknob[0] >= 3 and faderknob[1] == False:
		state.kn.faderknob[1] = True

	if mode == 0:
		if state.kn.hl_timecheck != 0:
			if not state.kn.midisplayrect: state.kn.set_mixer_rectangle()
			if time() - state.kn.hl_timecheck >= state.config.RangeRectTimer:
				state.kn.set_mixer_rectangle(1)
				state.kn.hl_timecheck = 0
		if state.config.FaderPickup and state.kn.has_pickup_active():
			state.kn.pickup_blink_handler()

	if state.config.SleepTimer:
		if state.kn.active[1]:
			if time() - state.kn.active[0] > state.config.SleepTimer * 60:
				state.kn.pause(2)	# Abort pause animation
				if mode == 0: state.kn.set_smr_status()	# Reset track lights
			state.kn.active[0] = time()
			state.kn.active[1] = False
		elif time() - state.kn.active[0] > state.config.SleepTimer * 60 and time() - state.kn.active[2] > 2:
			if getTrackPeaks(0,2) > 0: 
				state.kn.active[1] = True
				state.kn.active[0] = time()
			if not state.kn.active[1]: state.kn.pause(1)
