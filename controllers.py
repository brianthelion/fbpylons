import graphapi
import restapi

from pylons import config
from pylons import request
from pylons.controllers.util import redirect_to

APIKEY = config['facebook.apikey']
SECRET = config['facebook.secret']
APPID = config['facebook.appid']
CALLBACK = config['facebook.callback']

def get_postauth_url() : return CALLBACK

def get_auth_url() :
	
	postauth_url = get_postauth_url()
	return 'https://graph.facebook.com/oauth/authorize?client_id=%s&redirect_uri=%s' % (APPID,postauth_url)

class FacebookController(object) :
	
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
		return super( FacebookController,self ).__init__( *args,**dargs )
	
	def get_user( self ) :
		
		if self.user is None : # either we haven't tried 'getting' the user yet or we're somewhere in the middle of the auth sequence
			
			# assume we're in the middle of the auth sequence, and that the cookies will contain what we need
			self.user = graphapi.get_user_from_cookie(request.cookies, APIKEY, SECRET)
			
			if self.user is None :
			# turns out that we were NOT in the middle of the auth sequence, so we have to initiate it
				return self.redirect_to_auth()
		
		else : pass
				
			
	def redirect_to_login( self ) : pass
	
	def redirect_to_auth( self ) :
	
		'''See http://developers.facebook.com/docs/authentication/'''
		return redirect_to( get_auth_url() )
	
	def redirect_to_perms( self ) : pass
	
	def fbredirect( self,url ) : pass

class ExtendedProfileController( FacebookController ) : pass

#######################################################

from decorator import decorator

@decorator
def require_user(fn,ctrl,*args,**dargs) :

	if ctrl.user is not None : return fn(ctrl,*args,**dargs)
	else : return ctrl.get_user()

#@decorator
#def require_login(fn,ctrl,*args,**dargs) :
#	
#	if ctrl.user is not None : return fn(ctrl,*args,**dargs)
#	else : return ctrl.redirect_to_auth()
	
@decorator
def require_added(fn,ctrl,*args,**dargs) :

	if ctrl.user.added_application : return fn(ctrl,*args,**dargs)
	else : return ctrl.redirect()

def require_perms(*perms) :

	@decorator
	def wrapper(fn,ctrl,*args,**dargs) :

		if ctrl.user.fb.users.hasAppPermission(*perms) : return fn(ctrl,*args,**dargs)
		else : return ctrl.fb.request_extended_permission(*perms)
	
	return wrapper

@decorator
def require_exist(fn,ctrl,*args,**dargs) :
	
	if not dargs.has_key('uid') or ctrl.QL.userExists(dargs['uid']) : return fn(ctrl,*args,**dargs)
	else : return ctrl.redirect404()

@decorator
def require_canvas(fn,ctrl,*args,**dargs) : return fn

@decorator
def require_ajax(fn,ctrl,*args,**dargs) : return fn
