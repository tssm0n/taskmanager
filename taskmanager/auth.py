from models import *
from flask import session
from flask.ext.restless import ProcessingException

def check_auth():
    #TODO: This is a login workaround
    app.logger.debug("Single user mode...")
    #if not session.has_key('user'):
    session['user'] = User.query.get(1)
    return True

def api_auth(search_params=None, **kw):
    if not check_auth():
        raise ProcessingException(message='Not Authorized', status_code=401)
    if search_params is None:
        return

    # TODO: Filter the results based on the user ID
    # example: 
    # Create the filter you wish to add; in this case, we include only
    # instances with ``id`` not equal to 1.
    #filt = dict(name='id', op='neq', val=1)
    # Check if there are any filters there already.
    #if 'filters' not in search_params:
    #    search_params['filters'] = []
    # *Append* your filter to the list of filters.
    #search_params['filters'].append(filt)


class authed:
    def __init__(self, f):
	self.__name__ = f.__name__
        self.f = f
    
    def __call__(self):
        return self.f()
