import logging
log = logging.getLogger(__name__)

from pylons import request

import urllib
import simplejson
import cgi

import config

TOKEN_BASE_URL = 'https://graph.facebook.com/oauth/access_token?'
AUTH_BASE_URL = 'https://graph.facebook.com/oauth/authorize?'

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
