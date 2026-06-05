import app_state as state


def on_update_beat_indicator(beat):
	blink = True
	if not state.config.BlinkFullTempo:
		if beat == 0: blink = False
	if blink:
		state.kn.blink_transp_light('lighttoggle')

	
def on_update_meters():
	if state.config.PeakMeter: state.nm.main()
