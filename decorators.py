from decorator import decorator
import controllers

@decorator
def check_controller(fn,ctrl,*args,**dargs) :

	if not isinstance(ctrl,controllers.FBPylonsController) : raise Exception()
	else : return fn(ctrl,*args,**dargs)

@decorator
def require_fbuser(fn,ctrl,*args,**dargs) :

	if ctrl.user is not None : return fn(ctrl,*args,**dargs)
	else :
		ctrl.init_user()
		return fn(ctrl,*args,**dargs)

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
