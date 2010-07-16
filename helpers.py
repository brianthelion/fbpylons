import logging
log = logging.getLogger(__name__)

from pylons import config
from pylons import request
from pylons import url as old_url
from decorator import decorator

import urllib
import simplejson

FQL_BASE_URL = 'https://api.facebook.com/method/fql.query'

def require(test) :

	'''This should only be used on Controller methods'''

	@decorator
	def wrapper(fn,ctrl,*wargs,**wdargs) :
		
		result = test(ctrl)
		if result is True : return fn(ctrl,*wargs,**wdargs)
		else : return result
		
	return wrapper

def url(*args,**dargs) :
	
	qualified,fb = True,True

	if not dargs.has_key('qualified') :
		dargs['qualified'] = qualified

	if dargs.has_key('fb') :
		fb = dargs['fb']
		del dargs['fb']
	
	fn = None
	if len(args) == 0 : fn = old_url.current
	else : fn = old_url
	
	if fb : return fn( *args,**dargs ).replace(config['facebook.callbackurl'],config['facebook.canvasurl'])
	else : return fn( *args,**dargs )

def redirect(route,**dargs) :
	
	next_url = url(route,**dargs)
	
	if request.params.has_key('fb_sig_in_canvas') and request.params['fb_sig_in_canvas'] == '1' :
		log.debug( 'REDIRECT : %s' % (next_url,) )
		return '<fb:redirect url="%s" />' % next_url
	else :
		log.debug( 'REDIRECT : %s' % (next_url,) )
		return redirect_to( next_url )

def retrieve_objs( url,**dargs ) :
	
	log.debug( 'helpers.retrieve_objs %s %s' % (url,dargs) )

	url = url + '?' + urllib.urlencode(dargs)
	
	data = urllib.urlopen( url ).read()
	log.debug( 'helpers.retrieve_objs %s' % (data,) )
	
	objs = simplejson.loads( data )
	log.debug( 'helpers.retrieve_objs %s' % (objs,) )
	
	return objs
	
def fql_query( query_string,token ) :
	
	log.debug( 'fql_query: %s' % (query_string,) )
	
	args = {}
	args['query'] = query_string
	args['access_token'] = token
	args['format'] = 'json'

	return retrieve_objs( FQL_BASE_URL,**args )

