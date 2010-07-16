import logging
log = logging.getLogger(__name__)

from pylons import request, config
import helpers as h
import urllib

TOKEN_BASE_URL = 'https://graph.facebook.com/oauth/access_token?'
AUTH_BASE_URL = 'https://graph.facebook.com/oauth/authorize?'
EXCHANGE_BASE_URL = 'https://graph.facebook.com/oauth/exchange_sessions'

class FBAppUser(object) :

	def __init__(self) :
		
		self.uid = None
	
	def via_facebook(self) 		: raise NotImplementedError()
	def via_ajax(self) 		: raise NotImplementedError()
	def in_canvas(self) 		: raise NotImplementedError()
	def logged_in(self) 		: raise NotImplementedError()
	def added_app(self) 		: raise NotImplementedError()
	def gave_perms(self,*perms) 	: raise NotImplementedError()
	def auth(self,*perms) 		: raise NotImplementedError()

class RestUser(FBAppUser) :
	
	def via_facebook(self) :
		
		for k in request.params.keys() :
			if k.startswith( 'fb_sig_' ) : return True
			
		return False
	
	def in_canvas(self) : return request.params.has_key('fb_sig_in_canvas') and request.params['fb_sig_in_canvas'] == '1'
	
	def logged_in(self) :
		
		if request.params.has_key( 'fb_sig_logged_out_facebook' ) and request.params['fb_sig_logged_out_facebook'] == '1' : return False
		else : return True
	
	def added_app(self) : return request.params.has_key('fb_sig_added') and request.params['fb_sig_added'] == '1'

	def gave_perms(self,*perms) :
		
		if not request.params.has_key( 'fb_sig_ext_perms' ) : return False
		
		want = set(perms)
		got = set( request.params['fb_sig_ext_perms'].split(',') )
		
		return want <= got

class CanvasAppUser(RestUser) :
	
	def auth(self,*perms) :

		def already_authed(user) :
			
			log.debug('already_authed'), user.access_token is not None
			return user.access_token is not None

		def token_from_session(user) :
			
			log.debug('token_from_session')
			if request.params.has_key('session') :
				
				user.session = simplejson.loads( request.params['session'] )
				print user.session
				return True
				
			else : return False
		
		def redirect_to_auth(user) :
			
			log.debug('redirect_to_auth')
			
			args = {}
			args['client_id'] = config['facebook.appid']
			args['redirect_uri'] = h.url()
			
			if perms :
				args['scope'] = ','.join(perms)
			
			auth_url = AUTH_BASE_URL + urllib.urlencode(args)
			
			log.debug( auth_url )
			return h.redirect( auth_url,qualified=False )
		
		return already_authed(self) or token_from_session(self) or redirect_to_auth(self)

class MigratingUser(CanvasAppUser) :

	def __init__( self ) :
		
		self.access_token = None
		self.uid = None
		
		if self.added_app() :
		
			self.uid = request.params['fb_sig_user']
			self.access_token = self.exchange_sessions( request.params['fb_sig_session_key'] )[0]['access_token']
	
	def auth_pages(self,*perms,pids=[]) :
		
		args = {}
		args['client_id'] = config['facebook.appid']
		args['redirect_uri'] = h.url()
		args['enable_profile_selector'] = 1
		
		if pids :
			args['select_pages_ids'] = pids
		
		auth_url = AUTH_BASE_URL + urllib.urlencode(args)
		
		return h.redirect( auth_url,qualified=False )
	
	def exchange_sessions( self,key ) :
		
		args = {}
		args['type'] = 'client_cred'
		args['client_id'] = config['facebook.appid']
		args['client_secret'] = config['facebook.appsecret']
		args['sessions'] = key
		
		return h.retrieve_objs( EXCHANGE_BASE_URL,**args)

WorkingUser = MigratingUser

################################################################################
"""
class RedirectRequired( Exception ) : pass

class AuthorizationHandler( object ) :
	
	def __init__( self,ctrl ) :
		
		self.ctrl = ctrl
	
	def handle( self ) : raise NotImplemented()

class BasicAuthorizationHandler( AuthorizationHandler ) :

	'''
	This AuthorizationHandler should be fit for use in most stateless applications.
	
	I'm not really sure why this Hanlder works, but it does.
	1) It searches the request parameters for an existing Facebook session.
	2) If the session exists, it uses it.
	3) Otherwise, it pushes the user to the authorization page, telling the authorization
		page to redirect back to the canvas URL (eg, http://apps.facebook.com/myapp)
		when finished (This really shouldn't work according to the Facebook
		documentation. By my understanding, you should have redirect to something in
		your Connect domain (eg, http://mydomain.com/myapp). But you don't.)
	4) As long as the user has authorized the app, the session should now be present.
	'''

	def handle( self ) :
		
		if self.ctrl.user is not None : pass
		elif request.params.has_key('session') : 
			
			log.debug('Request contains "session": %s' % (request.params['session'],) )
			self.init_user_from_session()
			
		else :
			log.debug('Request does not contain "session"')
			return self.authorize_session()

	def init_user_from_session( self ) :
		
		log.debug( 'init_user_from_session' )
		self.ctrl.user = simplejson.loads( request.params['session'] )
	
	def authorize_session( self ) :

		log.debug( 'request_authcode' )

		args = {}
		args['client_id'] = config.APPID
		args['redirect_uri'] = config.CANVASURL
		
		auth_url = AUTH_BASE_URL + urllib.urlencode(args)
		
		raise RedirectRequired( auth_url )

################################################################################

class ServersideAuthorizationHanlder( BasicAuthorizationHandler ) :

	def handle( self ) :
	
		if self.ctrl.user is not None : pass
		elif request.params.has_key('session') : 
			
			log.debug('Request contains "session": %s' % (request.params['session'],) )
			self.init_user_from_session()
			
		elif request.params.has_key('code') :
			
			log.debug('Request does not contain "session"')
			log.debug('Request contains "code": %s' % (request.params['code'],) )
			
			self.init_session_from_code()
			self.init_user_from_session()
			return
			
		else :
			log.debug('Request does not contain "session"')
			log.debug('Request does not contain "code"')
			return self.request_authcode()
				
	def init_user_from_session( self ) :
		
		log.debug( 'init_user_from_session' )
		self.ctrl.user = simplejson.loads( request.params['session'] )
	
	def init_session_from_code( self ) :

		log.debug( 'init_session_from_code' )

		args = {}
		
		args['code'] = request.params['code']
		args['type'] = 'client_cred'	# have no idea why you have to do this, but you do
		args['client_id'] = config.APPID
		args['redirect_uri'] = 'http://apps.facebook.com/climbingtoday/'
		args['client_secret'] = config.APPSECRET
		
		token_url = TOKEN_BASE_URL + urllib.urlencode(args)
		response = cgi.parse_qs( urllib.urlopen( token_url ).read() )
		
		if response.has_key( 'error' ) : raise Exception( response['error'] )
		elif response.has_key( 'access_token' ) : raise 
	
	def request_authcode( self ) :

		log.debug( 'request_authcode' )

		args = {}
		args['client_id'] = config.APPID
		args['redirect_uri'] = 'http://apps.facebook.com/climbingtoday/'
		
		auth_url = AUTH_BASE_URL + urllib.urlencode(args)
		
		raise RedirectRequired( auth_url )

class CookieAuthorizationHandler( BasicAuthorizationHandler ) : pass
"""
