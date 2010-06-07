'''
At some point, I'd like this __init__ file to be smart enough to do all the
relevant edits to routing.py, middleware.py, etc, etc.
'''

REQUIRED = ['facebook.apikey','facebook.secret','facebook.callback','facebook.url']

def check_config() :
	
	from pylons import config
	class ConfigError(Exception) : pass	

	if not all( [config.has_key(r) for r in REQUIRED] ) : raise ConfigError()
	if not all( [config[r] for r in REQUIRED] ) : raise ConfigError()
	
check_config()

del check_config
del REQUIRED
