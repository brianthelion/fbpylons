'''
= Design notes =

In Pylons, it seems to be an unstated rule that Controller should only have
methods that map directly to URLs. Hence, we try not to clutter up the
Controller too much.

Instead, we move most of the Facebook-related code out two places:

	a) Controller mix-in classes for some basic infrastructure
	b) Decorators for the per-url Controller methods
	c) Event handlers triggered by the decorators

= Basic Usage =

1) Add a Controller mix-in to your Controller.

2) Apply decorators to your Controller's methods, in particular those that get
called from your routing map (config/routing.py)

3) Overload the various Hanlders to customize the bahavior that gets triggered
by the decorators

= To Do =

At some point, I'd like this __init__ file to be smart enough to do all the
relevant edits to routing.py, middleware.py, etc, etc.
'''

REQUIRED = ['facebook.apikey','facebook.appsecret','facebook.appid','facebook.callbackurl','facebook.canvasurl']
OPTIONAL = ['facebook.postauthurl']

def init() :

	def check_config() :
	
		from pylons import config
		class ConfigError(Exception) : pass

		error_str = 'fbpylons requires that the following variables be set in your development.ini: %s. For details, see the Facebook API documentation.' % ( ', '.join(REQUIRED), )
		
		if not all( [config.has_key(r) for r in REQUIRED] ) : raise ConfigError(error_str)
		if not all( [config[r] for r in REQUIRED] ) : raise ConfigError(error_str)
	
		extraneous = []
		for k in config.keys() :
			if k.startswith('facebook.') and k not in REQUIRED and k not in OPTIONAL : extraneous.append(k)
	
		if len(extraneous) > 0 : raise ConfigError( extraneous )

	def set_config() :
	
		from pylons import config, app_globals
	
		new_config = {}
		for k in config.keys() :
		
			if k.startswith('facebook.') : setattr( app_globals, k[9:].upper(), config[k] )

	def do_overloads() : pass

	check_config()
#	set_config()
	do_overloads()
