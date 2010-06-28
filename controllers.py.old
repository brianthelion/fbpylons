import graphapi
import restapi
import simplejson

from pylons import config
from pylons import request
from pylons.controllers.util import redirect_to

APIKEY 		= config['facebook.apikey']
APPSECRET 	= config['facebook.appsecret']
APPID 		= config['facebook.appid']
CALLBACKURL 	= config['facebook.callbackurl']

################################################################################

class FBPylonsController( object ) : pass

################################################################################

class RestController( FBPylonsController ) : pass

################################################################################

def get_facebook_config() : return { 'callbackurl':CALLBACKURL, 'appid':APPID, 'appsecret':APPSECRET, 'apikey':APIKEY }

def get_postauth_url() :
	
	# if a postauth URL is given, we should redirect there
	# else we should redirect to the page that needed the auth in the first place
	
	if config.has_key('facebook.postauthurl') : return config['facebook.postauthurl']
	else : return request.url

def get_auth_url(*perms) :
	
	postauth_url = get_postauth_url()
	auth_url = 'https://graph.facebook.com/oauth/authorize?client_id=%s&redirect_uri=%s' % (APPID,postauth_url)
	return auth_url

class GraphController( FBPylonsController ) :
	
	'''This is a mix-in class for Pylons controllers. Cannot be used stand-alone.'''

#	def __init__( self,*args,**dargs ) :
#		
#		user = graphapi.get_user_from_cookie(request.cookies, APIKEY, SECRET)
#		if user :
#			graph = graph.GraphAPI(user["oauth_access_token"])
#			profile = graph.get_object("me")
#    			friends = graph.get_connections("me", "friends")
#		
#		return super( FacebookController,self ).__init__( *args,**dargs )

	def __init__( self,*args,**dargs ) :
		
		self.user = None
		self.config = get_facebook_config()
		return super( GraphController,self ).__init__( *args,**dargs )
	
	def init_user( self,*perms ) :
		
#		print request.params
#		print request.cookies
		
		if self.user is None : # either we haven't tried 'getting' the user yet or we're somewhere in the middle of the auth sequence
			
#			print 'user is None'
			
			# assume we're in the middle of the auth sequence, and that the cookies will contain what we need
			#self.user = graphapi.get_user_from_cookie(request.cookies, APIKEY, SECRET)
			
			if request.params.has_key('session') : self.user = simplejson.loads(request.params['session'])
			else : return self.redirect_to_auth(*perms)
			
#			if self.user is None :
#			# turns out that we were NOT in the middle of the auth sequence, so we have to initiate it
#				print 'user is still None'
#				return self.redirect_to_auth(*perms)

		else : pass
				
			
	def redirect_to_login( self ) : pass
	
	def redirect_to_auth( self,*perms ) :
	
		'''See http://developers.facebook.com/docs/authentication/'''
		return redirect_to( get_auth_url(*perms) )
	
	def redirect_to_perms( self ) : pass
	
	def fbredirect( self,url ) : pass
	
	def postauth( self,nexturl=None ) : pass

################################################################################

class FacebookController( GraphController ) : pass

class ExtendedProfileController( FacebookController ) : pass

###############################################################################
