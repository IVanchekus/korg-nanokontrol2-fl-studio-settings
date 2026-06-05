# name=MAIN KORG nanoKONTROL2 (korg-nanokontrol2-fl-studio-settings)
# url=https://github.com/IVanchekus/korg-nanokontrol2-fl-studio-settings

from device import hardwareRefreshMixerTrack, setHasMeters

import app_state as state
from init_config import init_config
from nanometer import NanoMeter
from kontrol import Kontrol
from handlers.control_change import on_control_change
from handlers.idle import on_idle
from handlers.refresh import on_refresh
from handlers.meters import on_update_beat_indicator, on_update_meters


def OnInit():
	init_config()
	state.nm = NanoMeter()
	state.kn = Kontrol()
	hardwareRefreshMixerTrack(-1)
	if state.config.PeakMeter:
		setHasMeters()


def OnDeInit():
	if state.script_ready():
		if state.config.BracketedRange:
			state.kn.rename_range(0)
		if state.config.ColoredRange:
			state.kn.set_range_color(1)
		if state.config.RangeDisplayRect:
			state.kn.set_mixer_rectangle(1)
	state.kn = None
	state.nm = None


def OnControlChange(event):
	on_control_change(event)


def OnIdle():
	on_idle()


def OnRefresh(flags):
	on_refresh(flags)


def OnUpdateBeatIndicator(beat):
	on_update_beat_indicator(beat)


def OnUpdateMeters():
	on_update_meters()
