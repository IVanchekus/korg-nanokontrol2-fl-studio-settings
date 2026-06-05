DEFAULT_TOLERANCE = 0.015


def cc_to_volume(cc):
	volume = cc / 127 - 0.003
	if volume < 0.01:
		return 0
	if volume > 0.99:
		return 1
	return volume


def volumes_match(cc, fl_volume, tolerance=DEFAULT_TOLERANCE):
	if cc is None:
		return False
	return abs(cc_to_volume(cc) - fl_volume) <= tolerance


def slot_cc_value(ftune_volume, slot):
	if slot < 0 or slot >= len(ftune_volume):
		return None
	return ftune_volume[slot]
