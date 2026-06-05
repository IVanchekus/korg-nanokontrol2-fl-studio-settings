TRACK_SELECT = (0, 1)
MARKERS = (3, 4, 5)
TRANSPORT = (6, 7, 8, 9, 10)
KNOBS = (11, 12, 13, 14, 15, 16, 17, 18)
SMR_BUTTONS = tuple(range(19, 43))
FADERS = (43, 44, 45, 46, 47, 48, 49, 50)
CYCLE_BUTTON = 2

SMR_LIGHT_ROWS = (
	(19, 20, 21), (22, 23, 24), (25, 26, 27), (28, 29, 30),
	(31, 32, 33), (34, 35, 36), (37, 38, 39), (40, 41, 42),
)


def smr_cc_indices(key):
	SMR = 'SMR'
	if key in SMR:
		if key == SMR[0]: k = 1
		elif key == SMR[1]: k = 2
		elif key == SMR[2]: k = 3
		else: raise ValueError("key argument must be one of the strings 'S', 'M' or 'R'")
	return [3 * x + k for x in range(6, 14)]
