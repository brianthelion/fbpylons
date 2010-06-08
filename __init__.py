'''
At some point, I'd like this __init__ file to be smart enough to do all the
relevant edits to routing.py, middleware.py, etc, etc.
'''

REQUIRED = ['facebook.apikey','facebook.secret','facebook.callback','facebook.url','facebook.appid']

def check_config() :
	
	from pylons import config
	class ConfigError(Exception) : pass

	error_str = 'fbpylons requires that the following variables be set in your development.ini: %s. For details, see the Facebook API documentation.' % ( ', '.join(REQUIRED), )

	if not all( [config.has_key(r) for r in REQUIRED] ) : raise ConfigError(error_str)
	if not all( [config[r] for r in REQUIRED] ) : raise ConfigError(error_str)
	
check_config()

del check_config
del REQUIRED

import controllers
