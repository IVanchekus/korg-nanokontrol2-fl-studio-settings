from device import getPortNumber
from general import getVersion

import app_state as state


def init_config():
	state.config = None
	config = None
	options = {
		'MIDIChannel': 1, 'TransportChan': 14, 'SleepTimer': 5, 'HighlightColor': -11835046, 'MixerMode': True, 'ChannelrackMode': True,
		'PlaylistMode': True, 'ControllerLinkMode': False, 'PlayBlinkTempo': True, 'PeakMeter': True, 'PlayingOnly': False, 'ReversePeak': False,
		'BigMeter': False, 'Clipping': True, 'SelectedPeak': False, 'ArmedTracks': False, 'MultiSelect': False, 'TrackRangeOnly': False,
		'StickyMaster': False, 'RangeDisplayRect': True, 'ColoredRange': True, 'BracketedRange': False, 'TempoBase': 80, 'PreserveMixDiff': False,
		'BlinkFullTempo': False, 'RangeRectTimer': 0, 'ModeBlink': True, 'ChannelRectCtrl': False, 'TranspBtnLink': False, 'LinkOverriding': False,
		}
	numparams = {
		'MIDIChannel': (1,16), 'TransportChan': (1,16),'SleepTimer': (0,300),'HighlightColor': (-15461356,-1),'TempoBase':(10,397), 'RangeRectTimer': (0,10),
		'MIDIChannel_Unit2': (1,16),'TransportChan_Unit2': (1,16),'Port_Unit2': (0,255),
		'MIDIChannel_Unit3': (1,16),'TransportChan_Unit3': (1,16),'Port_Unit3': (0,255),
		'MIDIChannel_Unit4': (1,16),'TransportChan_Unit4': (1,16),'Port_Unit4': (0,255)
		}
	boolparams = options.keys() - numparams.keys()

	try: import config as user_config
	except Exception as e: print('nanometer config: ' + str(e) +'.')
	else: config = user_config

	if not config:
		print('nanometer config: using default options.')
		class Config: pass
		config = Config()

		for param in options:
			setattr(config,param,options[param])
	else:
		missing = []
		for param in boolparams:
			if hasattr(config,param):
				value = getattr(config,param)
				if type(value) is not bool:
					print('nanometer config: '+ param +' option is incorrectly set (must be True or False).')
					delattr(config,param)

		for param in numparams:
			if hasattr(config,param):
				value = getattr(config,param)
				if type(value) is not int:
					print('nanometer config: '+ param +' option is incorrectly set (must be a number).')
					delattr(config,param)
				elif value not in range(numparams[param][0],numparams[param][1]+1):
					print('nanometer config: '+ param +' option requires a number between ' + str(numparams[param][0]) +' and ' + str(numparams[param][1]) +'.')
					delattr(config,param)

		for param in options:
			if not hasattr(config,param):
				setattr(config,param,options[param])
				missing.append(param)

		if 'MultiSelect' in missing:
			if hasattr(config,'ExclusiveSelect'):
				value = getattr(config,'ExclusiveSelect')
				if type(value) is bool:
					setattr(config,'MultiSelect',not value)
					missing.remove('MultiSelect')

		if missing: print('nanometer config: using default value for ' +', '.join(missing) +'.')
		else: print('nanometer config: imported ok.')

	for u in range(2,5):
		m_bool = hasattr(config,'MIDIChannel_Unit'+str(u))
		t_bool = hasattr(config,'TransportChan_Unit'+str(u))
		p_bool = hasattr(config,'Port_Unit'+str(u))
		if m_bool & t_bool & p_bool:
			if getPortNumber() == getattr(config,'Port_Unit'+str(u)):
				config.MIDIChannel = getattr(config,'MIDIChannel_Unit'+str(u))
				config.TransportChan = getattr(config,'TransportChan_Unit'+str(u))

	if not hasattr(config,'Debug'): config.Debug = False
	if hasattr(config,'RangeDisplayRect') and config.RangeDisplayRect == True:
		if getVersion() >= 17:
			config.ColoredRange = False
		else:
			print('Error: RangeDisplayRect option requires a newer version of FL Studio.')
			config.RangeDisplayRect = False

	state.config = config
