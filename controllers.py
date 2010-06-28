import graphapi
import restapi
import handlers

#import simplejson

#from pylons import config
#from pylons import request
#from pylons.controllers.util import redirect_to

################################################################################

class FBPylonsController( object ) : pass

################################################################################

class RestController( FBPylonsController ) : pass

################################################################################

class GraphController( FBPylonsController ) :
	
	'''This is a mix-in class for Pylons controllers. Cannot be used stand-alone.'''

	def __init__( self,*args,**dargs ) :
		
		self.user = None
		
		if dargs.has_key('auth') : self.auth_handler_class = dargs['auth']
		else : self.auth_handler_class = handlers.BasicAuthorizationHandler
		
		return super( GraphController,self ).__init__( *args,**dargs )
	
	def redirect( self,url ) : return '<fb:redirect url="%s" />' % url
	
################################################################################

class FacebookController( GraphController ) : pass

###############################################################################
