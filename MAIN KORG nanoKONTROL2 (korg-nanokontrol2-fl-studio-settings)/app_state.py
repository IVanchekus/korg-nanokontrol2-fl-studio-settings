config = None
nm = None
kn = None


def script_ready():
	return config is not None and kn is not None and nm is not None
